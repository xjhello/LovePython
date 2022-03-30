#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/3/23 0023 11:48
@Author  : Xu_Jian
"""
import Queue
import json
import math
import threading
import time
import uuid
import gevent
import redis

from AMR.BaseClass.ReadWriteLock import global_lock
from AMR.tools.lockout.CalculationBase import AMRCalculation

from AMR.tools.lockout.LockoutModel import get_locked_area_move, get_locked_area_turning
from AMR.BaseClass.MessageDataWrapper import MessageDataWrapper
from AMR.tools.RcsHttpTool import RcsHttpTool
from AMR.tools.lockout.CalculateLockArea import LockAreaCalculate
from Cmds import CarrierCmd
from Context.ContextDsp import context_dsp
from AMR.BaseClass.MessageBase import MessageTypeEnum, MessageBase, MessageTemp
from Utils.HubRedis import QsHubRedis
from Utils.log import log_Communication, log_change, log_AMR_RUNING, log_Data
from settings.conf import params_props

if params_props.get("agvType") == "FORKLIFT":
    # 堆高车型特定的锁闭
    from AMR.RobotPlugin.FORKLIT.LockedAreaFactory import Graphics
    from AMR.lock_area.LockedAreaGenerate import LockGeneration
elif params_props.get("agvType") == "WORKBIN":
    from AMR.lock_area.LockedAreaGenerate import LockGeneration
elif params_props.get("agvType") == "QINGLUAN":
    from AMR.RobotPlugin.QINGLUAN.LockedAreaFactory import Graphics
    from AMR.lock_area.LockedAreaGenerate import LockGeneration
    from AMR.RobotPlugin.QINGLUAN.config import *
else:
    # from AMR.tools.lockout.LockedAreaFactory import Graphics
    from AMR.lock_area.LockedAreaGenerate import LockGeneration
import AMR.tools.Qsh_error_code
from AMR.tools.RobotErrorCodeTool import report_robot_error_code

try:
    from AMR.tools.lockout.LockingTools import locked_area, move_locked_area, locked_area_register
    from AMR.tools.lockout.LockArea import move_lock_area, location_lock_area, move_heading_lock_area, arc_move_lock_area
except Exception as e:
    log_Communication.error("import error:{}".format(e))

result_state = {'ACCEPTED': 1, 'FINISHED': 2, 'REFUSED': 3, 'FAILED': 4, 'CANCEL': 5}

# 操作Redis的临时做法,后期应走公共模块统一操作
HubRedis = QsHubRedis()

Angle_Start = -18000
Angle_End = 18000
Angle_Circle = 36000
Angle_Circle_Half = 18000
Angle_Circle_Quarter = 9000
Angle_Zero = 0


class AMRTask(MessageBase, AMRCalculation):
    """
    AMR任务分发处理中心 提供了与TestCommunication交互数据的一个PUSH端和一个PULL端
    将所有任务进行分发至子类任务执行器,所有的子类任务均是以附加任务的形式存在，故当前的AmrMove暂时写在TestTaskCenter中后期考虑也单独从该部分抽离出去
    负责调度和结果回调至TestCommunicatin层，剥离业务的具体执行
    """
    def __init__(self):
        # http接口查询器
        self.queryer = RcsHttpTool()
        # 锁闭区域计算工具
        self.lock_calculator = LockAreaCalculate()
        self.agvCode = str(params_props.get("agvCode"))
        self.agv_length = float(params_props.get("agv_length"))
        self.agv_height = int(params_props.get("agv_height"))
        self.data_wrapper = MessageDataWrapper()
        # 正在执行的任务
        self.doing_task = None
        # 任务的状态 0为接受  1为doing  2为失败  3位成功
        self.task_status = False
        # 坐标单位 默认1为m;0.001为mm
        self.position_unit = 1
        # 设备点
        self.device_dict = {}
        # 路径点处理
        self.point_dict = {}
        # 路径处理
        self.paths_dict = {}
        # 设备交互路径
        self.cooperations_roads_dict = {}
        # 外设交互请求id
        self.cooperation_request_id = None
        # 外设交互请求结果
        self.cooperation_request_res = None
        self.path_map_info = {}
        # 存储路径集合中的最后一段路径信息
        self.last_path_info = {}
        # 附加动作前的最后一段路径是否修改为路径终点的引导点
        self.go_to_guide_point = False
        # 引导点距离设备的距离 用于计算出路径上的引导点 m
        self.guide_distance = 1.35
        # 申请的锁闭区域是否被切
        self.request_region_truncate = False
        self.lockout_request_id = None
        self.lockout_response_id = None
        # 附加任务
        self.attachOperationList = Queue.Queue()
        self.region_request_id = None
        self.area = None
        self.is_doing = False
        # 上下文的redis订阅者
        self.redis_cmd_subscriber = redis.StrictRedis(host="127.0.0.1", port="26379").pubsub()
        # 有换向需求的路的下标
        self.turning_load_index = None
        # 换向点坐标
        self.turningCode = None
        # 换向角度
        self.dest_rack_heading = None
        #  接受来自中心的消息
        self.task_recv_from_center = Queue.Queue()
        self.task_send_to_center = Queue.Queue()
        threading.Thread(target=self.start_recv).start()
        threading.Thread(target=self.cmd_subscriber).start()

    def schedule_task(self, action):
        """调度task执行对象"""
        try:
            log_Communication.info('任务调度')
            if self.is_doing:
                log_Communication.info('任务正在执行中')
                log_AMR_RUNING.info('任务正在执行中')
                self.sender(self.action_status_response(action, result_state["REFUSED"]))  # 正在执行 拒绝action
                return
            self.is_doing = True
            # action信息放在redis
            context_dsp.add_redis_data("AMR:action", action)
            # 路径信息集合
            path_list = action['objects'][0]['value']['move']
            # 路径编码集合
            run_path_list = []
            for i in path_list["lineList"]:
                run_path_list.append(i["lineCode"])
            # 附带动作集合
            attach_operation = action['objects'][0]['value']['operation']
            # 降下的时候需要货架码
            # if attach_operation["name"] == "MOVE_LIFT_UP" or attach_operation["name"] == "MOVE_PUT_DOWN":
            if attach_operation["name"] in ["MOVE_LIFT_UP", "MOVE_PUT_DOWN", "WorkbinMoveFork", "WorkbinMovePutDown"]:
                # 是不是盲顶
                is_blind_lift = attach_operation["params"].get("isBlindLift", False)
                # 附加动作里的货架码
                rack_code = attach_operation["params"]["rackCode"]
                if not rack_code:
                    log_Communication.info("rackCode key not exist, may be is blind lift, set default blank str")
                    rack_code = ""
                # 附加动作里的数字码 数字码和货架码都是标识货架的，上位机和识别模块认可的是数字码，但RMS强制要求货架码所以出现了两个码！
                digital_code = attach_operation["params"].get("digitalCode")
                if not digital_code:
                    log_Communication.info("digitalCode key not exist, may be is blind lift, set default blank str")
                    digital_code = ""
                # 货架类型 新一轮商定后RMS会将货架类型传给上位机，上位机后续可以根据这个货架类型去查询到一些尺寸信息
                rack_type_code = attach_operation["params"]["rackTypeCode"]
                log_Communication.info("RMS下发的货架码:{} 数字码:{} 货架类型:{}".format(rack_code,digital_code,rack_type_code))
                log_AMR_RUNING.info("RMS下发的货架码:{} 数字码:{} 货架类型:{}".format(rack_code, digital_code, rack_type_code))
                # 将RMS下发的是不是盲顶货架编码和货架数字码实时存入redis 货架类型
                context_dsp.add_redis_data("AMR:RACK:rackCode", rack_code)
                context_dsp.add_redis_data("AMR:RACK:digitalCode", digital_code)
                context_dsp.add_redis_data("AMR:RACK:isBlindLift", is_blind_lift)
                context_dsp.add_redis_data("AMR:RACK:rackTypeCode", rack_type_code)

            # 堆高车货架码及托盘信息
            if attach_operation["name"] == "MOVE_FORK_UP" or attach_operation["name"] == "MOVE_FORK_DOWN":
                # # 附加动作里的货架码
                # rack_code = attach_operation["params"]["rackCode"]
                # # 附加动作里的数字码
                # digital_code = attach_operation["params"]["digitalCode"]
                # # 货架类型
                # rack_type_code = attach_operation["params"]["rackTypeCode"]
                # 托盘编码
                plt_code = attach_operation["params"]["palletCode"]
                # 托盘类型
                plt_type_code = attach_operation["params"]["palletTypeCode"]
                abutment_code = attach_operation["params"]["abutmentCode"]
                # log_Communication.info("RMS下发的堆高车货架码:{} 数字码:{} 货架类型:{}".format(rack_code, digital_code, rack_type_code))
                # log_AMR_RUNING.info("RMS下发的堆高车货架码:{} 数字码:{} 货架类型:{}".format(rack_code, digital_code, rack_type_code))
                log_Communication.info("RMS下发的堆高车托盘码:{} 托盘类型:{}".format(plt_code, plt_type_code))
                log_AMR_RUNING.info("RMS下发的堆高车托盘码:{} 托盘类型:{} 载体编码:{}".format(plt_code, plt_type_code,abutment_code))

                # 货架码、数字码、托盘码、托盘类型添加到redis
                # context_dsp.add_redis_data("AMR:FORK_RACK:rackCode", rack_code)
                # context_dsp.add_redis_data("AMR:FORK_RACK:digitalCode", digital_code)
                context_dsp.add_redis_data("AMR:FORK_PLT:plt_code", plt_code)
                context_dsp.add_redis_data("AMR:FORK_PLT:plt_type_code", plt_type_code)
                context_dsp.add_redis_data("AMR:FORK_PLT:abutment_code",abutment_code)

            if params_props.get("agvType") == "QINGLUAN" and attach_operation["name"] in [ql_action_move_change_height]:
                # 青鸾边移动边升降指令，需要提前将托盘高度放到redis中，计算锁闭的时候，从redis中取
                target_height = attach_operation["params"]["changedTargetHeight"]
                context_dsp.add_redis_data("AMR:QINGLUAN:targetHeight", target_height)
            else:
                context_dsp.add_redis_data("AMR:QINGLUAN:targetHeight", 0)

            # 执行任务 原点和非原点操作统一入口
            results = self.update_runtime_moveinfo(path_list["lineList"])  # 根据不同的附加动作 计算改变路径最后的目标点的位置
            if not results:
                log_Communication.info("路径计算错误")
                log_AMR_RUNING.info("路径计算错误")
                self.sender(self.action_status_response(action, result_state["FAILED"]))
                self.is_doing = False
            else:
                log_Communication.info("路径计算成功")
                self.task_execute(action)

        except Exception as e:
            log_Communication.error("run_rms_task error:{}".format(e),exc_info=True)

    def task_execute(self, action):
        """
        任务执行
        """
        try:

            # 回复接受任务
            self.sender(self.action_status_response(action, result_state["ACCEPTED"]))
            # 执行层
            if params_props.get("agvType") == "FORKLIFT":
                from AMR.RobotPlugin.FORKLIT.TaskHandler1 import TaskHandler
            elif params_props.get("agvType") == "QINGLUAN":
                from AMR.RobotPlugin.QINGLUAN.TaskHandler import TaskHandler
            elif params_props.get("agvType") == "WORKBIN":
                from AMR.RobotPlugin.WORKBIN.TaskHandler import TaskHandler
            else:
                from AMR.core.TaskHandler import TaskHandler

            action = context_dsp.get_redis_data("AMR:action")
            # 原点移动和非原点移动统一分发
            # 判断是否是特殊的路径编码或者路径为空
            run_path_list = [i for i in action['objects'][0]['value']['move']]
            if len(run_path_list) == 0:
                # 特殊的路径移动
                log_Communication.info("原点移动")
                self.special_task_execute(action)
                return
            task_handler = TaskHandler()
            # 由于路径重规划会在锁闭申请的时候下发 所以要在重规划后重载数据
            results = task_handler.handle_task()
            log_Communication.info("任务执行结果：{}".format(results))
            log_AMR_RUNING.info("任务执行结果：{}".format(results))

            # 这里需要特殊处理 是否是任务取消的失败  还是执行的失败  判断依据为redis的值
            if results:
                self.is_doing = False
                # 执行结束后 不论成功与否 申请原地锁闭
                log_Communication.info("完成任务后停车")
                log_AMR_RUNING.info("完成任务后停车")
                if self.apply_robot_area():
                    self.sender(self.action_status_response(action, result_state["FINISHED"]))
                    log_Communication.info("完成任务后停车锁闭成功")
                    log_AMR_RUNING.info("完成任务后停车锁闭成功")
                else:
                    self.sender(self.action_status_response(action, result_state["FAILED"]))
                    log_Communication.info("完成任务后停车失败")
                    log_AMR_RUNING.info("完成任务后停车锁闭失败")
                HubRedis.add("AMR:RMSMove", "")
                HubRedis.add("AMR:RMSOperation", "")
                HubRedis.add("AMR:pathVersion", "")

                return

            # 返回执行结果失败了  有两种情况。一是正常失败 二是路径重规划了 需要结束当前的任务
            else:
                # 判断是否是路径重规划，看redis的RTSErrorCode是否是RTS000003
                # 还有一种情况为任务干预的取消 这个时候需要特殊判断
                if HubRedis.get("AMR:TaskState") == "CANCEL":
                    log_Communication.info("任务取消的失败。不回复任务任务失败, 立即停止")
                    log_AMR_RUNING.info("任务取消的失败。不回复任务任务失败, 立即停止")
                    self.is_doing = False
                    log_Communication.info("回复任务取消完成 并且锁闭")
                    log_AMR_RUNING.info("回复任务取消完成 并且锁闭")
                    if self.apply_robot_area():
                        log_Communication.info("任务取消完成锁闭成功")
                        log_AMR_RUNING.info("任务取消完成锁闭成功")
                    else:
                        log_Communication.info("任务取消完成锁闭失败")
                        log_AMR_RUNING.info("任务取消完成锁闭失败")
                    HubRedis.add("AMR:RMSMove", "")
                    HubRedis.add("AMR:RMSOperation", "")
                    HubRedis.add("AMR:pathVersion", "")
                    HubRedis.add("AMR:RTSErrorCode", "")
                    self.sender(self.action_status_response(action, result_state["CANCEL"]))
                    return

                if HubRedis.get("AMR:RTSErrorCode") == "RTS000003":
                    log_Communication.info("路径重规划的失败，不回复任务任务失败，更新路径生成新的task执行")
                    log_Communication.info("递归入口")
                    self.task_execute(action)
                    # log_Communication.info("路径重规划后的任务执行结果：{}".format(results))
                    HubRedis.add("AMR:RMSMove", "")
                    HubRedis.add("AMR:RMSOperation", "")
                    HubRedis.add("AMR:pathVersion", "")
                    HubRedis.add("AMR:RTSErrorCode", "")
                    return

                else:
                    self.is_doing = False
                    # 回复任务失败后申请故障锁闭
                    log_Communication.info("当前回复任务失败向RMS申请故障锁闭")
                    if self.apply_robot_area():
                        log_Communication.info("故障锁闭成功")
                        log_AMR_RUNING.info("故障锁闭成功")
                    else:
                        log_Communication.info("故障锁闭失败")
                        log_AMR_RUNING.info("故障锁闭失败")
                    HubRedis.add("AMR:RMSMove", "")
                    HubRedis.add("AMR:RMSOperation", "")
                    HubRedis.add("AMR:pathVersion", "")
                    self.sender(self.action_status_response(action, result_state["FAILED"]))
                    return

        except Exception as e:
            self.is_doing = False
            log_Communication.info("异常递归结束:{}".format(e))

            HubRedis.add("AMR:RMSMove", "")
            HubRedis.add("AMR:RMSOperation", "")
            HubRedis.add("AMR:pathVersion", "")
            log_Communication.error('task_scheduler ERROR{}'.format(e),exc_info=True)
            log_AMR_RUNING.info('task_scheduler ERROR{}'.format(e))

    def special_task_execute(self, action):
        """
        特殊移动，特殊处理，现在是原点到原点
        """
        try:
            # 回复接受任务
            # self.sender(self.action_status_response(action, result_state["ACCEPTED"]))
            # 特殊任务处理  原点到原点没有路径  特征是lineCode这空  不在地图中
            if params_props.get("agvType")=="FORKLIFT":
                from AMR.RobotPlugin.FORKLIT.TaskHandler1 import TaskHandler
            elif params_props.get("agvType")=="QINGLUAN":
                from AMR.RobotPlugin.QINGLUAN.TaskHandler import TaskHandler
            elif params_props.get("agvType")=="WORKBIN":
                from AMR.RobotPlugin.WORKBIN.TaskHandler import TaskHandler
            else:
                from AMR.core.TaskHandler import TaskHandler
            task_handler = TaskHandler()
            task = action['objects'][0]['value']
            results = task_handler.handle_no_line_code_task(task)
            if results:
                self.is_doing = False
                # 执行结束后 不论成功与否 申请原地锁闭
                log_Communication.info("完成任务后停车")
                if self.apply_robot_area():
                    self.sender(self.action_status_response(action, result_state["FINISHED"]))
                    log_Communication.info("完成任务后停车锁闭成功")
                else:
                    log_Communication.info("完成任务后停车失败")
                    self.sender(self.action_status_response(action, result_state["FAILED"]))
            else:
                self.is_doing = False
                # 回复任务失败后申请故障锁闭
                log_Communication.info("当前回复任务失败向RMS申请故障锁闭")
                if self.apply_robot_area():
                    log_Communication.info("故障锁闭成功")
                else:
                    log_Communication.info("故障锁闭失败")
                self.sender(self.action_status_response(action, result_state["FAILED"]))
        except Exception as e:
            log_Communication.error('task_scheduler ERROR{}'.format(e))

    def cmd_subscriber(self):
        """订阅来自context的cmd消息"""
        try:
            log_Communication.info("listen1")
            self.redis_cmd_subscriber.subscribe("ARM:cmd_stats")
            log_Communication.info("listen2")
            while True:
                msg = self.redis_cmd_subscriber.parse_response()
                # 埋点日志格式要求  [datas=>$#” json “#$]
                # log_Communication.info("接收redis的发布消息：{}".format(msg))
                # content = [{"time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                #             "agvId": self.agvCode, "msg": msg}]
                # log_mode = {"version": 1.0, "generator": "upper_computer", "type": "agv_lockzone_record", "content": content}
                # log_Communication.info("[datas=>$#{}#$]".format(log_mode))
                if msg[0] == "message":
                    data = json.loads(msg[-1])
                    content = [{"time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "agvId": self.agvCode, "msg": data}]
                    log_mode = {"version": 1.0, "generator": "upper_computer", "type": "agv_lockzone_record", "content": content}
                    # log_Data.info("DSP执行时间: {}".format(log_mode))
                    log_Data.info("[datas=>$#{}#$]".format(log_mode))
                    # ['message', 'ARM:cmd_stats', '{"cmd_name": "DoMove", "command_stats": 1, "command_id": 3}']
                    self.report_cmd_status(cmd_name=data["cmd_name"], command_id=data["command_id"],
                                           command_stats=data["command_stats"])

        except Exception as e:
            log_Communication.error("cmd_subscriber：{}".format(e))

    def start_recv(self):
        """
        消息中心的work,所有PUSH的消息都在经过这个分发
        """
        while True:
            data = self.task_recv_from_center.get()
            # 接收消息后，做不同的处理操作
            threading.Thread(target=self.message_handler, args=(data,)).start()
            # self.message_handler(data)

    def sender(self, data):
        """
        发送接口
        """
        # threading.Thread(target=self.push_socket.send, args=json.dumps(data))
        if data["messageType"] == "RequestLockedArea":
            # 如果是锁闭数据存入redis供3D显示
            context_dsp.add_redis_data("AMR:LockArea", data)
        self.task_send_to_center.put(json.dumps(data))

    def report_cmd_status(self, cmd_name, command_id=0, command_stats=1):
        """上报指令执行情况"""
        """
          string msgId = 1;
          string robotCode = 2;
          string eventName = 3;
          string commandId = 4;
          string commandStats = 4;
        """
        data = {
            "msgId": str(HubRedis.get("AMR:TaskMsgId")),
            "robotCode": str(self.agvCode),
            "eventName": str(cmd_name),
            "commandId": str(command_id),
            "commandState": str(command_stats),
        }
        message_report = MessageTemp(data=data, messageType=MessageTypeEnum.ReportCmdStatus)  # ReportCmdStatus
        # log_Communication.info("上报指令执行情况: {}".format(message_report))
        self.task_send_to_center.put(json.dumps(message_report))

    def message_handler(self, message):
        """
        消息处理
        """
        message = self.formatter(message)
        if message.messageType == MessageTypeEnum.ResponseLockedArea:
            # 锁闭回复
            # log_Communication.info("TCP 锁闭回复 ：{}".format(message))
            if message.result:
                # log_Communication.info("TCP 锁闭成功")
                # 锁闭区域数据
                self.area = message.data["layers"]  # 所有的layers
                self.region_request_id = message.id
                # 是否被RTS区域切割
                self.request_region_truncate = message.data["truncated"]
            else:
                # 监控失败了
                log_Communication.info("TCP 锁闭失败")
                self.area = None  # 所有的layers
                self.region_request_id = message.id

        # 路径重规划
        elif message.messageType == MessageTypeEnum.PathPlan:
            # 重规划的路径应该是基于当前路径的修改, 下标为当前路径的下标
            pathplan_list = message.data['data']["lineList"]
            log_Communication.info("Task处理重规划的路径：{}".format(pathplan_list))
            # 调用重新读取路径信息的接口
            self.update_runtime_moveinfo(pathplan_list, is_path_replan=True)
            # 更新pathVserion
        # 外设交互回复
        elif message.messageType == MessageTypeEnum.CooperationResponse:
            if message.result:
                log_Communication.info("外设交互请求成功")
                if message.data["request_result"]:
                    log_Communication.info("外设交互回复结果成功")
                    self.cooperation_request_res = True
                else:
                    self.cooperation_request_res = False
            else:
                log_Communication.info("外设交互回复失败")
                self.cooperation_request_res = False
            self.cooperation_request_id = message.id

        elif message.messageType == MessageTypeEnum.OffLine:
            log_Communication.info("收到下线将 is_doing置为False")
            self.is_doing = False
        else:
            log_Communication.info("未知信息 :{} ".format(message))

    def search_charge_line_point(self, equipment_code):
        '''
        根据工作点或者设备点 查找与充电桩相联的唯一路点 一般只有一条路
        '''
        equip_code_info = self.point_dict.get(equipment_code)
        charge_heading = equip_code_info[1].get("heading")  # heading为充电桩设备在地图中的朝向
        if not charge_heading:
            log_Communication.error("设备点没有充电朝向参数heading, 读取chargingHeading做heading 做反转")
            temp_dict = {0: 180, 90: -90, 180: 0, -90: 90}
            charge_heading = equip_code_info[1].get("chargingHeading")
            if not charge_heading:
                log_Communication.error("没有充电桩属性chargingHeading")
                return "", []
            charge_heading = temp_dict.get(int(charge_heading))
        charge_heading = float(charge_heading)
        target_point = ""
        target_coordinates = []
        equip_x, equip_y = equip_code_info[0][0], equip_code_info[0][1]
        for line in self.search_lines_base_point(equipment_code):
            point_list = self.lines_dict.get(line)
            # 一条线有两个点  列表长度为2 根据一个索引 取出另一个点
            other_point = point_list[1 - point_list.index(equipment_code)]
            _coordinates = self.point_dict.get(other_point)  # 一条线上另一个点坐标列表
            _coordinates = _coordinates[0]
            # other_point_x, other_point_y, other_point_z = _coordinates[0], _coordinates[1], _coordinates[2]
            # v1 = [equip_x, equip_y, other_point_x, other_point_y]
            # # 创建离当前点200mm外的虚拟数据 为了计算向量夹角
            # # 先地图0度做为参考系
            # v2 = [equip_x, equip_y, 200 * math.cos(0) + equip_x, 200 * math.sin(0) + equip_y]
            # target_angle = self.get_vector_angle(v1, v2)
            # if target_angle == 90:  # 如果夹角是90度，有可能不清楚是y的正方向还是负方向 以90度做为参考系做为判断  地图角度-90即可
            #     v3 = [equip_x, equip_y, 200 + math.cos(90) + equip_x, 200 * math.sin(90) + equip_y]
            #     tmp_angle = self.get_vector_angle(v1, v3)
            #     charge_heading = charge_heading - 90
            #     target_angle = tmp_angle
            # if abs(charge_heading - float(target_angle)) < 5:  # 向量夹角小于5度认为是要找的点
            #     target_point = other_point
            #     target_coordinates = _coordinates
            #     break
            target_point = other_point
            target_coordinates = _coordinates
            break
        return target_point, target_coordinates

    def search_lines_base_point(self, point_code):
        '''
        根据点编码查找相关的线，为了计算出需要的前一个点
        '''
        lines_list = []
        for line, points in self.lines_dict.items():
            if point_code in points:
                lines_list.append(line)
        return lines_list

    def judge_lock_area_status(self, request_id):
        """
        判断锁闭回复的统一工具
        """
        # 等待锁闭回复
        for i in range(100):
            gevent.sleep(0.5)
            log_Communication.info("发送的id：{}, 接受的id：{}".format(request_id, self.region_request_id))
            if request_id == self.region_request_id:
                return True, self.area
        return False, None

    def action_status_response(self, action, result_index):
        '''
        生成action的回复状态  result_state = {'ACCEPTED': 1, 'FINISHED': 2, 'REFUSED': 3, 'FAILED': 4}
        '''
        # 检查是否是任务取消的错误
        flag = HubRedis.get("AMR:TaskState")
        if flag == "CANCEL":
            log_Communication.info("任务取消的回复！")
            action_value = action["objects"][0]["value"]
            status_response = {"msgId": action_value["msgId"],
                               "robotCode": self.agvCode,
                               "resultIndex": result_state['CANCEL'],
                               "createTime": int(time.time() * 1000)}
            response_id = str(uuid.uuid4())
            action_response_message = MessageTemp(id=response_id, messageType=MessageTypeEnum.ReportTaskStatus,
                                                  data=status_response)
            HubRedis.add("AMR:TaskState", "None")
            return action_response_message

        action_value = action["objects"][0]["value"]
        status_response = {"msgId": action_value["msgId"],
                           "robotCode": self.agvCode,
                           "resultIndex": result_index,
                           "createTime": int(time.time() * 1000)}
        log_Communication.info("回复RMS任务情况:{}".format(status_response))
        response_id = str(uuid.uuid4())
        action_response_message = MessageTemp(id=response_id, messageType=MessageTypeEnum.ReportTaskStatus,
                                              data=status_response)
        return action_response_message

    def apply_robot_area(self):
        """申请静止状况下的锁闭图形"""
        # from AMR.LockingTools import locked_area_register
        # 增加循环等待机器人不是doing中再申请锁闭，由其是在move接续过程中任务被取消，导致申请了锁闭，机器人还是向前跑了一段
        while True:
            gevent.sleep(0.15)
            if context_dsp.base_info.robot_state != 1:  # 1是doing中，其他情况代表机器人停止运动
                break
            else:
                log_Communication.info("等待0.15秒 当前指令执行完")
        log_Communication.info("申请停车的锁闭")
        graphics_id, point_list, start_point, end_point = 0, [], [], []
        if params_props.get("agvType") == "FORKLIFT":
            message_apply_locked_area, request_id = Graphics(graphics_id, point_list, start_point, end_point)
        elif params_props.get("agvType") == "QINGLUAN":
            message_apply_locked_area, request_id = Graphics(graphics_id, point_list, start_point, end_point)
        else:

            message_apply_locked_area, request_id = LockGeneration.match_area(graphics_id, start_point, end_point)
        # else:
        #     message_apply_locked_area, request_id = Graphics(graphics_id, point_list, start_point, end_point)
        log_Communication.info("area :{}   id:{} ".format(message_apply_locked_area, request_id))
        self.sender(message_apply_locked_area)
        # 返回的修改为一个字典
        return self.monitor_truncate_lockout(request_id)

    def check_and_lift(self, operation_params):
        """
        是否顶升前确认 + 顶升 + 是否顶升后确认 的执行集合
        """
        # 货架码
        rack_code = operation_params["rackCode"]
        #  是否顶升前确认
        is_check_before = operation_params["isCheckBefore"]
        # 是否顶升后确认
        is_check_after = operation_params["isCheckAfter"]
        # rack_info = self.queryer.query_shelf_data(rack_code)
        # # 货架长
        # rack_length = rack_info["length"]
        # # 货架宽
        # rack_width = rack_info["width"]
        # # 货架高
        # rack_height = rack_info["height"]
        log_Communication.info("是否顶升前确认:{} 是否顶升后确认:{}".format(is_check_before, is_check_after))
        if is_check_before == "true":
            log_Communication.info('开始执行顶升前确认')
            params_dict = dict()
            ret = context_dsp.run_base_sync_cmd(monitor=True, cmd_class_name="DoBucketCheckWithUpCameraBeforeLiftup",
                                                **params_dict)
            if ret:
                log_Communication.info("顶升前确认成功")
            else:
                log_Communication.error("顶升前确认失败")
                return False
        params_dict = dict(
            targetheight=1,
            guideflag=0,
        )
        lift_ret = context_dsp.run_base_sync_cmd(monitor=True, cmd_class_name="DoLiftUp", **params_dict)
        if lift_ret:
            log_Communication.info('顶升动作完成')
            if is_check_after == "true":
                log_Communication.info('开始顶升后确认')
                params_dict = dict()
                lift_after = context_dsp.run_base_sync_cmd(CarrierCmd.DoBucketCheckWithUpCameraAfterLiftup,
                                                           **params_dict)
                if lift_after:
                    log_Communication.info('顶升后确认完成')
                    log_Communication.info('搬货任务执行完成 回复任务完成')
                    return True
                else:
                    log_Communication.info('搬货任务执行失败 回复任务失败')
                    return False
            log_Communication.info('搬货任务执行完成 回复任务完成')
            return True
        else:
            log_Communication.info('搬货任务执行失败 回复任务失败')
            return False

    def real_blind_lift(self):
        params_dict = dict(
            targetheight=1,
            guideflag=0,
        )
        lift_ret = context_dsp.run_base_sync_cmd(monitor=True, cmd_class_name="DoLiftUp", **params_dict)
        if lift_ret:
            log_Communication.info("盲顶 顶升完成")
            log_Communication.info('盲顶 搬货任务执行完成 回复任务完成')
            return True
        else:
            log_Communication.error("盲顶 顶升失败")
            log_Communication.info('盲顶 搬货任务执行失败 回复任务失败')
            return False

    def put_down_operation(self):
        log_Communication.info("执行放货指令")
        params_dict = dict(
            targetheight=0,
            guideflag=0,
        )
        down_ret = context_dsp.run_base_sync_cmd(monitor=True, cmd_class_name="DoPutDown", **params_dict)
        if down_ret:
            log_Communication.info('放货任务执行完成')
            return True
        else:
            log_Communication.info('放货任务执行失败')
            return False

    def apply_for_lockout(self, graphics_id, point_list, start_point, end_point,headDir=200):
        """
        1. 矩形
        2. 矩形加终点圆
        3. 起点圆加矩形
        """
        if params_props.get("agvType") == "FORKLIFT":
            message_apply_locked_area, request_id = Graphics(graphics_id, point_list, start_point, end_point)
        elif params_props.get("agvType") == "QINGLUAN":
            message_apply_locked_area, request_id = Graphics(graphics_id, point_list, start_point, end_point)
        else:

            message_apply_locked_area, request_id = LockGeneration.match_area(graphics_id, start_point, end_point,headDir=headDir)
        # else:
        #     message_apply_locked_area, request_id = Graphics(graphics_id, point_list, start_point, end_point)
        log_Communication.info("area :{}   id:{} ".format(message_apply_locked_area, request_id))
        self.sender(message_apply_locked_area)
        # 返回的修改为一个字典
        return self.monitor_lockout(request_id)

    def apply_for_truncate_lockout(self, graphics_id, point_list, start_point, end_point, path_version=None,headDir=200):
        """
            考虑被裁剪的情况
        """
        # if params_props.get("agvType") == "FORKLIFT":
        if params_props.get("agvType") == "FORKLIFT":
            message_apply_locked_area, request_id = Graphics(graphics_id, point_list, start_point, end_point)
        elif params_props.get("agvType") == "QINGLUAN":
            message_apply_locked_area, request_id = Graphics(graphics_id, point_list, start_point, end_point)
        else:
            message_apply_locked_area, request_id = LockGeneration.match_area(graphics_id, start_point, end_point,headDir=headDir,point_list=point_list)
        # else:
        #     message_apply_locked_area, request_id = Graphics(graphics_id, point_list, start_point, end_point)
        # log_Communication.info("Task层 发送 锁闭区域 :{}   id:{} ".format(message_apply_locked_area, request_id))
        # log_Communication.info("Task层 发送 锁闭区域 ")
        self.sender(message_apply_locked_area)
        # 返回的修改为一个字典
        return self.monitor_truncate_lockout(request_id)

    def apply_for_outer_cooperation(self, data):
        # 发送给RMS
        request_id = str(uuid.uuid1())
        cooperation_message = MessageTemp(id=request_id, messageType=MessageTypeEnum.CooperationRequest, data=data)
        log_Communication.info("外设交互申请信息: {}".format(cooperation_message))
        self.sender(cooperation_message)
        return self.monitor_outer_cooperation(request_id)

    def monitor_outer_cooperation(self, request_id):
        """
        外设交互监控
        """
        try:
            while True:
                # 一直监控
                # TCP层发送相同的id后 就是监控到了交互的回复
                if self.cooperation_request_id == request_id:
                    if self.cooperation_request_res:  # 交互请求返回True
                        return True
                    else:  # 交互返回False
                        # todo 目前需要申请路径路径重规划
                        return False
                else:
                    # 未回复，等待中
                    gevent.sleep(0.15)
        except Exception as e:
            log_Communication.error("monitor_outer_cooperation", exc_info=True)

    def monitor_lockout(self, request_id):
        """监控锁闭申请ID"""
        log_Communication.info("监控id:{}  返回id: {}".format(request_id, self.region_request_id))
        for i in range(200):
            # log_Communication.info("监控id:{}  返回id: {}".format(request_id, self.region_request_id))
            if self.region_request_id == request_id:
                log_Communication.info("**" * 20)

                # 锁闭通过是否需要切
                lockout_resp = {
                    "result": True,  # 是否申请返回
                    "area": self.area,  # 返回的区域
                    "truncate": self.request_region_truncate  # 是否被裁剪
                }
                log_Communication.info("\n锁闭通过 ： {}\n".format(lockout_resp))
                return True

            time.sleep(0.2)
        log_Communication.info("**" * 20)
        log_Communication.info("\n超时锁闭失败\n")
        return False

    def monitor_truncate_lockout(self, request_id):
        """
            监控锁闭申请
        """
        try:
            while True:  # 一直监控中
                # log_Communication.info("监控id:{}  返回id: {}".format(request_id, self.region_request_id))
                # 根据request_id 监控是否有返回
                # TCP层发送相同的id后 就是监控到了锁闭的回复
                if self.region_request_id == request_id:
                    # log_Communication.info("当前area:{}".format(self.area))
                    # self.area是否为空 如果为None的话 就是失败了
                    if self.area:
                        # log_Communication.info("锁闭成功   self.area :{}".format(self.area))
                        log_Communication.info("task层判断锁闭成功")
                        return_points_list = self.area[0]['shapes'][1:] # 忽视本体锁闭图形
                        # log_Communication.info("return_points_list :{}".format(return_points_list))
                        POLYGON_point_obj = []
                        if return_points_list:
                            # 返回的可能包含了圆形，所以需要过滤掉圆形
                            for i in return_points_list:
                                # 返回的数据有时候为数字有时候是str！！！！！！
                                if i['type'] == 1 or i['type'] == "POLYGON":
                                    POLYGON_point_obj = i['points']

                        area_list = []
                        for i in POLYGON_point_obj:
                            tmp = []
                            tmp.append(i["x"])
                            tmp.append(i["y"])
                            area_list.append(tmp)
                        # 锁闭通过是否需要切监控id
                        lockout_resp = {
                            "result": True,  # 是否申请返回
                            "area": area_list,  # 返回的区域
                            "truncate": self.request_region_truncate  # 是否被裁剪
                        }
                        log_Communication.info("锁闭通过: {}\n".format(lockout_resp))
                        return lockout_resp
                    else:
                        log_Communication.warning("锁闭失败")
                        lockout_resp = {
                            "result": False,  # 是否申请返回
                            "area": self.area,  # 返回的区域
                            "truncate": self.request_region_truncate  # 是否被裁剪
                        }
                        log_Communication.info("Task层锁闭处理  返回的锁闭区域为空 :{} \n".format(lockout_resp))
                        return lockout_resp
                else:
                    # 未回复 等待中
                    time.sleep(0.15)

        except Exception as e:
            log_Communication.error("monitor_truncate_lockout :{}".format(e))

    def read_map(self):
        """读取map信息"""
        try:
            with open("/config/path_map.json", 'r') as f:
                map_info = json.load(f)
            self.point_list = []
            # k-路径id  v-坐标
            self.point_dict = {}
            # 点类型映射  k-点编码  v-点类型
            self.point_type_dict = {}
            point_index_list = map_info["points"][0]
            p_key_index = {key: index for index, key in enumerate(point_index_list)}

            # 点处理
            for i in map_info["points"][1:]:
                code = i[p_key_index["code"]]
                point_type = i[p_key_index["pointType"]]
                position = i[p_key_index["position"]]
                attrs = i[p_key_index["attrs"]]
                temp = {
                    'id': code,
                    'pointType': point_type,
                    'position': position,
                    'attrs': attrs
                }
                self.point_dict[code] = [position, attrs]
                self.point_list.append(temp)
                self.point_type_dict[code] = point_type
            # for i in map_info["points"][1:]:
            #     temp = {
            #         'id': i[0],
            #         'pointType': i[1],
            #         'position': i[2],
            #         'attrs': i[5]
            #     }
            #     self.point_dict[i[0]] = [i[2], i[5]]
            #     self.point_list.append(temp)
            # 点集合存入redis备用
            context_dsp.add_redis_data("RMS/point/list", self.point_list)

            # 线处理
            self.lines_list = []
            self.lines_dict = {}
            # 线编码映射线类型
            self.lcode2ltype = {}

            # 曲线控制点坐标：k-线编码 v-[[x1,y1],[x2,y2]]
            self.control_poionts = {}
            # 路径的所有扩展属性 形如{'Adb22z_jzk75r-pointLines_1': {'beforehandNotifyDistance': 10000, 'beforehandNotifyEnabled': True, 'followRobotEnabled': True}}
            self.path_extension_attr = {}
            lines_index_list = map_info["lines"][0]
            l_key_index = {key: index for index, key in enumerate(lines_index_list)}
            for i in map_info["lines"][1:]:
                l_code = i[l_key_index["code"]]
                l_points = i[l_key_index["points"]]
                l_position = i[l_key_index["code"]]
                l_type = i[l_key_index["lineType"]]
                # 线的属性  目前包括到曲线的控制点坐标
                l_attrs = i[l_key_index["attrs"]]
                if l_type == "ARC":
                    self.control_poionts[l_code] = l_attrs["referencePoints"]
                temp = {
                    'id': l_code,
                    'points': l_points,
                    'position': l_position,
                    'line_type': l_type,
                }
                self.lines_dict[l_code] = l_points
                self.path_extension_attr[l_code] = l_attrs
                self.lines_list.append(temp)
                self.lcode2ltype[l_code] = l_type
            # for i in map_info["lines"][1:]:
            #     temp = {
            #         'id': i[0],
            #         'points': i[3],
            #         'position': i[0],
            #     }
            #     self.lines_dict[i[0]] = i[3]
            #     self.lines_list.append(temp)
            """
            lines_dict : {'b8y2XY_7sP6eA-pointLines_23': [u'b8y2XY', u'7sP6eA']}
            point_dict : {u'RRaS6x': [2000, 2000, 0]} 
            lcode2ltype : {u'RRaS6x': "ARC"} 
            """
            # log_Communication.info("\n\n路径集合：{}  \n点位集合:{}\n\n".format(self.lines_dict, self.point_dict))
            # check_point = self.check_map_point_info()
            # if not check_point:
            #     report_message = report_robot_error_code.report_robot_error_message(
            #         [{"code": Qsh_error_code.PARSE_RCS_MAP_ERROR, "params": ""}])
            #     self.sender(report_message)
            # 获取交互路径信息
            self.get_cooperation_roads(map_info)
        except Exception as e:
            log_Communication.error("read_map Exception: {}".format(e))
            log_AMR_RUNING.error("read_map Exception: {}".format(e))
            report_message = report_robot_error_code.report_robot_error_message(
                [{"code": AMR.tools.Qsh_error_code.PARSE_RCS_MAP_ERROR, "params": ""}])
            self.sender(report_message)

    def get_cooperation_roads(self, map_info):
        """
        获取所有外设交互路径集合及所对应的信息，由路编码唯一标识做为key，value为交互相关的参数
        解析地图后生成的交互路径信息格式
        t = {
                "line_code":
                    [
                        {"LOGISTICS_DOOR": {
                            "equipmentCode": "xxx"
                        }},
                        {"UNIVERSAL": {
                            "startCommandData": "xx",
                            "startCommand": "xxx",
                            "lastCommandData": "xx",
                            "lastCommand": "xxx"
                        }}
                    ]
            }
        """
        # 地图文件中interactions键的第1个元素是对应后续元素所在的索引意义，json的hpack压缩算法形成的数据结构
        self.cooperations_roads_dict = {}
        cooperations_datas = map_info.get("cooperations")
        # 为None 代表地图中不存在交互路径，不添加self.cooperations_roads_dict 为空，交互路径检查为False
        # 也是保护后续解析地图取值不要报错
        if not cooperations_datas:
            log_Communication.info("地图中不存在交互路径")
            return True
        cooperations_index_list = map_info["cooperations"][0]
        coope_key_index = {key: index for index, key in enumerate(cooperations_index_list)}
        for i in map_info["cooperations"][1:]:
            cooperation_code = i[coope_key_index["code"]]  # 编号
            cooperation_type = i[coope_key_index["type"]]  # 设备类型
            cooperation_name = i[coope_key_index["name"]]  # 设备名字
            cooperation_position = i[coope_key_index["position"]]  # 设备坐标
            cooperation_zone_code = i[coope_key_index["zoneCode"]]  # 库区
            cooperation_attrs = i[coope_key_index["attrs"]]  # 设备相关属性
            bind_lines = cooperation_attrs["bindLines"]  # 设备绑定所在路上的集合
            tmp = {
                cooperation_type: {
                    "code": cooperation_code,
                    "name": cooperation_name,
                    "position": cooperation_position,
                    "zoneCode": cooperation_zone_code
                }
            }
            for line_code in bind_lines:
                if cooperation_type == "LOGISTICS_DOOR":  # 物流门
                    tmp[cooperation_type].update({
                        "equipmentCode": cooperation_attrs.get("equipmentCode", "")
                    })
                else:  # 通用
                    tmp[cooperation_type].update({
                        "startCommand": cooperation_attrs.get("startCommand", ""),
                        "startCommandData": cooperation_attrs.get("startCommandData", ""),
                        "lastCommand": cooperation_attrs.get("lastCommand", ""),
                        "lastCommandData": cooperation_attrs.get("lastCommandData", "")
                    })
                if line_code in self.cooperations_roads_dict:  # 路编码已经添加过
                    self.cooperations_roads_dict[line_code].append(tmp)
                else:  # 第一次添加进去成列表
                    self.cooperations_roads_dict[line_code] = [tmp]
        log_Communication.info("all interactions roads: {}".format(self.cooperations_roads_dict))

    def check_map_point_info(self):
        '''
        校验点集合是不是正确
        '''
        for key, value in self.point_dict.items():
            if not all(value):
                return False
        return True

    def update_runtime_moveinfo(self, path_list, is_path_replan=False):
        """
        更新移动过程中所需要的信息，包括第一次移动和路径重规划移动
        path_list: lineList
        更新信息为原子性操作 需要加写锁
        """
        try:
            # 更改redis值时添加锁
            global_lock.acquire()
            # 更新redis中的action
            action_data = context_dsp.get_redis_data("AMR:action")
            action_data["move"]["lineList"] = path_list
            context_dsp.add_redis_data("AMR:action", action_data)
            # path_list = path_list["lineList"]
            log_Communication.info("\n规划的路径:{} \n".format(path_list))
            # 获取线编码
            run_path_list = []
            for i in path_list:
                run_path_list.append(i["lineCode"])

            # 将移动得路径和动作设置为类属性其他地方会用
            self.run_path_list = run_path_list
            self.run_line_code = []
            # 移动动作点集合
            self.run_point_code = []
            self.all_road = []

            # 地图中点坐标单位为mm
            for line_info in path_list:
                # 获取路编码
                line_code = line_info["lineCode"]
                rackHeading = line_info["rackHeading"]
                robotHeading = line_info["robotHeading"]
                # log_Communication.info("路编码:{} 任务要求货架角度:{}".format(line_code, rackHeading))
                self.run_line_code.append(line_code)
                # 判断路编码是否在自身的地图中
                if not self.lines_dict.has_key(line_code):
                    # 路径重规划的时候 可能有原点移动 这个时候要处理下 无线编码不能报错继续解析
                    if is_path_replan:
                        log_Communication.info("路径重规划的原点移动")
                        global_lock.release()
                        return True
                    log_Communication.warning("!!" * 20)
                    log_Communication.warning("地图中不存在此路径 {} \n\n".format(line_code))
                    report_message = report_robot_error_code.report_robot_error_message(
                        [{"code": AMR.tools.Qsh_error_code.PLAN_PATH_NOT_EXIST, "params": str(line_code)}]
                    )
                    self.sender(report_message)
                    global_lock.release()
                    return False
                # 路编码找码编码
                start_point_code = self.lines_dict[line_code][0]
                end_point_code = self.lines_dict[line_code][1]
                # 点编码查找点类型
                start_point_type = self.point_type_dict[start_point_code]
                end_point_type = self.point_type_dict[end_point_code]
                # 码编码找码坐标 单位mm
                start_point = self.point_dict[start_point_code][0][:-1]
                end_point = self.point_dict[end_point_code][0][:-1]
                # 点编码查找路径的类型
                path_type = self.lcode2ltype[line_code]
                # 添加点集合
                self.run_point_code.append([start_point, end_point])

                road = {
                    # 路径编码
                    "path_code": line_code,
                    # 起点坐标
                    "start_point": start_point,
                    # 起点编码
                    "start_point_code": start_point_code,
                    # 起点点类型
                    "start_point_type": start_point_type,
                    # 终点坐标
                    "end_point": end_point,
                    # 终点编码
                    "end_point_code": end_point_code,
                    # 终点点类型
                    "end_point_type": end_point_type,
                    # 计算锁闭区域
                    "locked_area": self.lock_calculator.get_rectangle_contain_agv(start_point[0], start_point[1],
                                                                                  end_point[0],
                                                                                  end_point[1]),
                    # 车头方向
                    "heading_direction": self.get_slope(start_point[0], start_point[1], end_point[0], end_point[1]),

                    # 此条路上的货架角度
                    "shelf_angle": self.get_shelf_angle(line_code),

                    # 系统期望的货架角度
                    "expected_shelf_angle": int(rackHeading),
                    # 系统期望的机器人角度角度
                    "expected_robot_angle": int(robotHeading),

                    # 地图中的货架角度
                    "map_shelf_angle": line_info["rackHeading"],

                    # 路径类型 当前分为直线和曲线
                    "path_type": path_type,
                    # 曲线的控制点坐标  通过线编码获取控制点
                    "control_points": self.control_poionts[line_code] if path_type == "ARC" else [],
                    # 是否跟车
                    "whether_follow": self.path_extension_attr[line_code]["followRobotEnabled"] if self.path_extension_attr[line_code].has_key("followRobotEnabled") else False
                }
                log_Communication.info(
                    "路编码:{}  锁闭区域:{}   \n 任务要求货架角度:{}".format(line_code, road["locked_area"], rackHeading))
                self.all_road.append(road)

            # 把规划信息放到redis中 执行移动的时候也需要从redis中获取达到动态更新的功能
            HubRedis.add("AMR:AllRoad", json.dumps(self.all_road))
            log_change.info("计算的机器人路径信息：{}".format(self.all_road))
            global_lock.release()
            return True
        except Exception as e:
            log_Communication.error("更新运行时移动信息失败:{}".format(e))
            global_lock.release()
            report_message = report_robot_error_code.report_robot_error_message(
                [{"code": AMR.tools.Qsh_error_code.PARSE_RCS_MAP_ERROR, "params": ""}])
            self.sender(report_message)
            return False

    def last_path_end_point_base_operation(self, path_list, att_operation):
        '''
        根据附加动作计算最后一条路径的终点位置并返回最后路径的相关road数据

        path_list :"4XSYt3_CbewGp-pointLines_22"
        '''
        if not path_list:
            log_Communication.info("路径信息为空，不计算最后改变移支最后一个点")
            return
        log_Communication.info("由附加动作计算最后路径坐标点")
        operation_name = att_operation["name"]
        operation_params = att_operation["params"]
        if not operation_name:  # 没有附属动作
            log_Communication.info("没有附加任务 返回")
            return

        # 堆高车取放货task
        if operation_name == "MOVE_FORK_UP":
            l_line = self.lines_dict[path_list]  # [u'2G78mj']
            l_start_code = l_line[0]
            l_target_point_code = l_line[1]  # 2G78mj
            # 最后一条路径的起点坐标
            start_point = self.point_dict[l_start_code][0][:-1]
            # 最后一条路径的终点坐标
            target_point = self.point_dict[l_target_point_code][0][:-1]
            # 保存终点坐标
            # HubRedis.add("AMR:OldEndPoint", json.dumps(target_point))
            # 路径角度
            path_angle = self.get_slope(start_point[0], start_point[1], target_point[0], target_point[1])
            # 请求托盘信息
            tray_info = self.queryer.query_tray_data()
            if tray_info:
                if tray_info["forkBottomHeight"] == 0:
                    tray_length = tray_info["length"]
                else:
                    # 暂时测试数据写死
                    # tray_length = self.queryer.query_shelf_detail_data()["length"]
                    tray_length = 1000
                # 实际停车距离
                guide_distance = (params_props.get("agv_length", 1000) + tray_length) / 2 + 400
                # 最终停车坐标
                final_x = int(target_point[0] - guide_distance * math.cos(math.radians(path_angle)))
                final_y = int(target_point[1] - guide_distance * math.sin(math.radians(path_angle)))

                final_point = [final_x, final_y, 0]
                log_Communication.info("当前将目标点由：{}改为引导点：{}".format(target_point, final_point))
                end_point = final_point
                tar_road = {
                    "end_point": end_point,
                    "locked_area": self.lock_calculator.get_rectangle_contain_agv(start_point[0], start_point[1],
                                                                                  end_point[0],
                                                                                  end_point[1]),
                }
                all_road_from_redis = json.loads(HubRedis.get("AMR:AllRoad"))
                # 更新最后一条路径相关信息
                all_road_from_redis[-1].update(tar_road)
                HubRedis.add("AMR:AllRoad", json.dumps(all_road_from_redis))
            else:
                log_Communication.error("获取托盘信息失败，请检查数据！")
                return False

        # 堆高车取放货task
        if operation_name == "MOVE_FORK_DOWN":
            l_line = self.lines_dict[path_list]  # [u'2G78mj']
            l_start_code = l_line[0]
            l_target_point_code = l_line[1]  # 2G78mj
            # 最后一条路径的起点坐标
            start_point = self.point_dict[l_start_code][0][:-1]
            # 最后一条路径的终点坐标
            target_point = self.point_dict[l_target_point_code][0][:-1]
            # 保存终点坐标
            # HubRedis.add("AMR:OldEndPoint", json.dumps(target_point))
            # 路径角度
            path_angle = self.get_slope(start_point[0], start_point[1], target_point[0], target_point[1])
            # 请求货架信息
            exist_shelf = self.queryer.query_exists_shelf_at_end_point(l_target_point_code)
            if not exist_shelf:
                log_Communication.info("当前存在附加动作放货, 但RMS告知目标终点无货架 不修改目标点坐标")
                return False
            else:
                log_Communication.error("获取货架信息失败，请检查数据！")
                target_code_info = self.point_dict.get(l_target_point_code)
                guide_mode = target_code_info[1].get("guideMode", False)  # guideMode 为目标终点的引导方式
                log_Communication.info("目标终点的引导方式为:{}".format(guide_mode))

                HubRedis.add("AMR:targetGuideMode", json.dumps(guide_mode))
                if not guide_mode:
                    log_Communication.info("目标终点无引导方式 不修改目标位置")
                    return False
                # 路径角度
                path_angle = self.get_slope(start_point[0], start_point[1], target_point[0], target_point[1])
                # 查询货架尺寸信息
                shelf_info = self.queryer.query_shelf_detail_data()
                # 货架长
                rack_length = shelf_info["length"]
                # 货架宽
                rack_width = shelf_info["width"]
                # 货架高
                rack_height = shelf_info["height"]
                # 引导距离 即车在距离最终的目标点多少距离停车
                guide_distance = (params_props.get("agv_length", 1000) + rack_length) / 2 + 300
                final_x = int(target_point[0] - guide_distance * math.cos(math.radians(path_angle)))
                final_y = int(target_point[1] - guide_distance * math.sin(math.radians(path_angle)))
                final_point = [final_x, final_y]
                log_Communication.info("当前将目标点由：{}改为引导点：{}".format(target_point, final_point))
                end_point = final_point
                tar_road = {
                    "end_point": end_point,
                    "locked_area": self.lock_calculator.get_rectangle_contain_agv(start_point[0],
                                                                                  start_point[1],
                                                                                  end_point[0],
                                                                                  end_point[1]),
                }
                all_road_from_redis = json.loads(HubRedis.get("AMR:AllRoad"))
                # 更新最后一条路径相关信息
                all_road_from_redis[-1].update(tar_road)
                HubRedis.add("AMR:AllRoad", json.dumps(all_road_from_redis))

        # 堆高车充电task
        if operation_name == "CHARGE":
            log_Communication.info("充电任务")
            equipment_code = operation_params.get("equipmentPointCode")
            if not equipment_code:
                log_Communication.error("无法获取充电设备点编码, 使用充电工作点编码")
                equipment_code = operation_params.get("targetPointCode")
                if not equipment_code:
                    log_Communication.error("无法获取充电工作点编码, 不更改最后一条路径的终点")
                    return False

            l_line = self.lines_dict[path_list]  # [u'2G78mj']
            l_start_code = l_line[0]
            # 最后一条路径的起点坐标
            start_point = self.point_dict[l_start_code][0][:-1]
            # 充电任务: 冲电桩朝向及最后停靠点坐标计算
            heading, target_point = self.calculate_charge_offset_point(equipment_code)
            log_Communication.info("获取充电桩heading:{}, 停靠点:{}".format(heading, target_point))
            # 充电桩角度
            if heading is None:
                log_Communication.error("获取充电桩heading失败")
                return False

            charge_angle = float(heading)*1e-2 + 90
            # 圆整
            if charge_angle > 180:
                charge_point_angle = charge_angle - 360
            elif charge_angle < -180:
                charge_point_angle = charge_angle + 360
            else:
                charge_point_angle = charge_angle

            if len(target_point) < 2:
                log_Communication.error("无法计算充电附加任务移动的最后一条路径目标点")
                return False

            # 判断当前车的角度
            now_heading = context_dsp.base_info.agv_theta * 1e-2
            log_Communication.info("当前车的角度:{}, 堆高车充电角度:{}".format(now_heading, charge_point_angle))
            if abs(abs(now_heading) - abs(charge_point_angle)) >= 0.5:

                log_Communication.info("当前附加任务为堆高车充电且是slam真车 将车头旋转至与充电桩正交角度：{}".format(charge_point_angle))
                params = dict(
                    targetX=context_dsp.base_info.agv_x,
                    targetY=context_dsp.base_info.agv_y,
                    targetHeading=(charge_point_angle) * 100,
                )
                turn_res = context_dsp.run_base_sync_cmd('DoRotate', monitor=True, **params)
                log_Communication.info("充电移动前旋转执行结果:{}".format(turn_res))
                if not turn_res:
                    return False
            # 保存最后一段路径的角度
            HubRedis.add("AMR:target_charge_h", json.dumps(charge_point_angle))
            end_point = [int(i) for i in target_point]
            tar_road = {
                "end_point": end_point,
                "locked_area": self.lock_calculator.get_rectangle_contain_agv(start_point[0], start_point[1],
                                                                              end_point[0],
                                                                              end_point[1]),
            }
            all_road_from_redis = json.loads(HubRedis.get("AMR:AllRoad"))
            # 更新最后一条路径相关信息
            all_road_from_redis[-1].update(tar_road)
            HubRedis.add("AMR:AllRoad", json.dumps(all_road_from_redis))

    def judgment_on_arrival(self, target_x, target_y):
        """到点判断  当前车位置距离路径终点的距离  """
        while True:
            now_x = context_dsp.base_info.agv_x * 1e-3
            now_y = context_dsp.base_info.agv_y * 1e-3
            dis = self.two_point_distance(now_x, now_y, target_x * 1e-3, target_y * 1e-3)
            if dis < 1.5:
                return True
            else:
                log_Communication.info(
                    "到点判断 dis:{} now_x:{}  now_y:{}  t_x:{}  t_y:{} ".format(dis, now_x, now_y, target_x * 1e-3,
                                                                             target_y * 1e-3))
                time.sleep(1)

    def get_slope(self, x1, y1, x2, y2):
        """求两点的斜率"""
        # 返回为角度
        return math.degrees(math.atan2(y2 - y1, x2 - x1))
        # 返回为弧度
        # return math.atan2(y2 - y1, x2 - x1)

    def get_shelf_angle(self, path_code):
        """获取此条路上要求的货架角度"""
        # 通过路编码获取路上允许的货架角度
        # 假数据90度
        return 9000

    def apply_lockout_for_move(self, x1, y1, x2, y2, ):
        """
        直线移动锁闭 传入起点终点坐标  单位mm
        x1, y1 起点坐标 单位mm
        x2, y2 终点坐标 单位mm
        """
        agv_length = int(params_props.get("agv_length", 1000))
        # AGV长的一半
        long_radius = agv_length / 2
        angle = math.atan2(y2 - y1, x2 - x1)
        h = 0.4 * 1000
        point1_x = x1 - h * math.sin(angle)
        point1_y = y1 + h * math.cos(angle)

        point2_x = x2 - h * math.sin(angle)
        point2_y = y2 + h * math.cos(angle)

        point3_x = x2 + h * math.sin(angle)
        point3_y = y2 - h * math.cos(angle)

        point4_x = x1 + h * math.sin(angle)
        point4_y = y1 - h * math.cos(angle)

        # 基于AGV长的一半修改区域点坐标 目的是得到的区域包裹整个车身

        final1_x = point1_x - long_radius * math.cos(angle)
        final1_y = point1_y - long_radius * math.sin(angle)

        final2_x = point2_x + long_radius * math.cos(angle)
        final2_y = point2_y + long_radius * math.sin(angle)

        final3_x = point3_x + long_radius * math.cos(angle)
        final3_y = point3_y + long_radius * math.sin(angle)

        final4_x = point4_x - long_radius * math.cos(angle)
        final4_y = point4_y - long_radius * math.sin(angle)
        point_list = []
        point_list.append([final1_x, final1_y])
        point_list.append([final2_x, final2_y])
        point_list.append([final3_x, final3_y])
        point_list.append([final4_x, final4_y])

        # 封装直线移动锁闭区域的数据
        locked_request_data = get_locked_area_move(self.agvCode, point_list, x1, y1, x2, y2)

        # 发送给RMS
        request_id = str(uuid.uuid4())
        self.lockout_request_id = request_id
        message_apply_locked_area = MessageTemp(id=request_id, messageType=MessageTypeEnum.RequestLockedArea,
                                                data=locked_request_data)
        log_Communication.info("$$" * 10)
        log_Communication.info("发送的锁闭区域: {}".format(locked_request_data))
        log_Communication.info("$$" * 10)
        self.sender(message_apply_locked_area)
        return self.monitor_lockout(request_id)

    def apply_lockout_for_turning(self, x, y):
        """申请旋转区域"""
        locked_request_data = get_locked_area_turning(self.agvCode, x, y)
        request_id = str(uuid.uuid4())
        self.lockout_request_id = request_id
        message_apply_locked_area = MessageTemp(id=request_id, messageType=MessageTypeEnum.RequestLockedArea,
                                                data=locked_request_data)
        log_Communication.info("$$" * 10)
        log_Communication.info("发送的锁闭区域: {}".format(locked_request_data))
        log_Communication.info("$$" * 10)
        self.sender(message_apply_locked_area)
        return self.monitor_lockout(request_id)

    def apply_lockout_before_lift(self):
        """
        顶升前的锁闭申请
        """
        # 当前小车自身的锁闭区域
        now_agv_lock_area = self.lock_calculator.get_now_agv_lock_area()
        message_apply_locked_area, request_id = LockGeneration.match_area(5, 0, 0)
        # message_apply_locked_area, request_id = Graphics(5, now_agv_lock_area, 0, 0)
        log_Communication.info("顶升前申请area :{}   id:{} ".format(message_apply_locked_area, request_id))
        self.sender(message_apply_locked_area)
        # 返回的修改为一个字典
        return self.monitor_lockout(request_id)
    def apply_lockout_forklift_up(self):
        """
        堆高车取货后锁闭申请
        :return:
        """
        message_apply_locked_area, request_id = LockGeneration.adapt_forklift_area(5)
        log_Communication.info("叉取后申请area :{}   id:{} ".format(message_apply_locked_area, request_id))
        self.sender(message_apply_locked_area)
        # 返回的修改为一个字典
        return self.monitor_lockout(request_id)

    def apply_lockout_forklift_down(self):
        """
        堆高车放货后锁闭申请
        :return:
        """
        message_apply_locked_area, request_id = LockGeneration.adapt_forklift_area(8)
        log_Communication.info("放货后申请area :{}   id:{} ".format(message_apply_locked_area, request_id))
        self.sender(message_apply_locked_area)
        # 返回的修改为一个字典
        return self.monitor_lockout(request_id)

    def apply_lockout_after_lift(self):
        """
        顶升后的锁闭申请 需要附加声明特殊标识
        """
        now_agv_lock_area = self.lock_calculator.get_now_agv_lock_area()
        message_apply_locked_area, request_id = LockGeneration.match_area(6, 0, 0)
        # message_apply_locked_area, request_id = Graphics(6, now_agv_lock_area, 0, 0)
        log_Communication.info("顶升后申请area :{}   id:{} ".format(message_apply_locked_area, request_id))
        self.sender(message_apply_locked_area)
        # 返回的修改为一个字典
        return self.monitor_lockout(request_id)

    def apply_lockout_put_down(self):
        """
        放下动作后的锁闭申请 需要附加声明特殊标识
        """
        now_agv_lock_area = self.lock_calculator.get_now_agv_lock_area()
        message_apply_locked_area, request_id = LockGeneration.match_area(7, 0, 0)
        # message_apply_locked_area, request_id = Graphics(7, now_agv_lock_area, 0, 0)
        log_Communication.info("放下前申请area :{}   id:{} ".format(message_apply_locked_area, request_id))
        self.sender(message_apply_locked_area)
        # 返回的修改为一个字典
        return self.monitor_lockout(request_id)

    def apply_lockout_turning(self):
        """
        旋转动作的锁闭申请
        """
        now_agv_lock_area = self.lock_calculator.get_now_agv_lock_area()
        message_apply_locked_area, request_id = LockGeneration.match_area(8, 0, 0)
        # message_apply_locked_area, request_id = Graphics(8, now_agv_lock_area, 0, 0)
        log_Communication.info("旋转申请area :{}   id:{} ".format(message_apply_locked_area, request_id))
        self.sender(message_apply_locked_area)
        # 返回的修改为一个字典
        return self.monitor_lockout(request_id)

    def two_point_distance(self, x1, y1, x2, y2):
        """两点间距离"""
        dis = math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2))
        log_Communication.info("当前点：{}, {}   目标点:{}, {}   距离: {}".format(x1, y1, x2, y2, dis))
        return dis

    def calculate_charge_offset_point(self, equipment_code):
        '''
        计算充电 robot引导位置 主要是slam充电
        1，根据点编码查询地图中当前充电桩在地图上的朝向
        2，根据点的坐标和朝向 结合参数配置充电的引导的坐标
        '''
        try:
            equip_code_info = self.point_dict.get(equipment_code)
            charge_heading = equip_code_info[1].get("heading")  # heading为充电桩设备在地图中的朝向
            if not charge_heading:
                log_Communication.error("设备点没有充电朝向参数heading, 读取chargingHeading做heading")
                temp_dict = {0: 180, 90: -90, 180: 0, -90: 90}
                charge_heading = equip_code_info[1].get("chargingHeading")
                if not charge_heading:
                    log_Communication.error("没有充电桩属性chargingHeading")
                    return None, []
                charge_heading = temp_dict.get(int(charge_heading))
            charge_heading = float(charge_heading)
            equip_code_coordinate = equip_code_info[0]  # x, y, z
            charge_offset = float(params_props.get("forklift_charge_distance", 0.9)) * 1000
            # if charge_offset < (self.agv_length / 2):
            #     charge_offset = self.agv_length
            log_Communication.info("充电目标点坐标x:{}; y:{}".format(equip_code_coordinate[0], equip_code_coordinate[1]))
            tar_x = charge_offset * math.cos(math.radians(charge_heading)) + equip_code_coordinate[0]
            tar_y = charge_offset * math.sin(math.radians(charge_heading)) + equip_code_coordinate[1]
            return charge_heading, [tar_x, tar_y]
        except Exception as e:
            log_Communication.error("获取充电停靠点失败:{}".format(e))

def GetCross(x1, y1, x2, y2, x, y):
    """
    计算(x1,y1)(x,y)、(x2,y2)(x,y)向量的叉乘
    """
    a = (x2 - x1, y2 - y1)
    b = (x - x1, y - y1)
    return a[0] * b[1] - a[1] * b[0]


def isInSide(x1, y1, x2, y2, x3, y3, x4, y4, x, y):
    return GetCross(x1, y1, x2, y2, x, y) * GetCross(x3, y3, x4, y4, x, y) >= 0 \
           and GetCross(x2, y2, x3, y3, x, y) * GetCross(x4, y4, x1, y1, x, y) >= 0


amr_task = AMRTask()

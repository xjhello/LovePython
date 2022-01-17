#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/7/15 15:17
@Author  : Xu_Jian
"""
import json

from google.protobuf.json_format import MessageToJson, Parse, ParseDict, MessageToDict

from grpcDemo.protobuf.msg import AgvAction_pb2
from grpcDemo.protobuf.msg.MessageBase_pb2 import MessageBase
# from msg import AgvAction_pb2


# 序列化
# 生成动作对象
agv_obj = AgvAction_pb2.AgvActionMessage()

agv_obj.agvAction.agvId = "agvid"
# 注意  枚举类型  第一个值为默认的值， 默认值不显示....
# agv_obj.messageBase.messageTypeEnum = 1
agv_obj.messageBase.messageTypeEnum = 2
agv_obj.messageBase.mapping.path = "/action"
agv_obj.messageBase.mapping.modeEnum = 1
agv_obj.messageBase.mapping.typeEnum = MessageBase.Model.REQUEST
agv_obj.messageBase.respTimeoutMillis = 666

# MessageToJson 消息转json str
print("type: {}  value:{}".format(type(MessageToJson(agv_obj)), MessageToJson(agv_obj)))
# MessageToDict 消息转字典
print("type: {}  value:{}".format(type(MessageToDict(agv_obj)), MessageToDict(agv_obj)))

# ParseDict： Parses a JSON dictionary representation into a message
# 将 JSON 字典表示解析为消息 # 注意类型匹配
demo = ParseDict({"id":"12"}, MessageBase)
print("type: {}  value:{}".format(type(demo), demo))

# Parses : Parses a JSON representation of a protocol message into a message
# 将协议消息的 JSON 表示解析为消息
ss = '{"id":"12"}'
demo1 = Parse(ss, MessageBase)
print("type: {}  value:{}".format(type(demo1), demo1))

# SerializeToString  消息转成bytes
data_bytes = agv_obj.SerializeToString()
# data_bytes = AgvAction_pb2.AgvActionMessage().SerializeToString()
print("type: {}  value:{}".format(type(data_bytes), data_bytes))

# ParseFromString  bytes转成消息
# 注意 要得到一个反序列化后的对象 要先new 一个空对象 单纯序列化返回的之数据长度
data_message = AgvAction_pb2.AgvActionMessage().ParseFromString(data_bytes)
print("type: {}  value:{}".format(type(data_message), data_message))
recv_obj = AgvAction_pb2.AgvActionMessage()
recv_obj.ParseFromString(data_bytes)
print("type: {}  value:{}".format(type(recv_obj), recv_obj))

# 序列化：    字典 ---> 消息 ---> bytes
# 反序列化：  bytes ---> 消息  ---> 字典

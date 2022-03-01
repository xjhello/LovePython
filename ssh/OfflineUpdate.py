#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import os
import paramiko
import tarfile


def make_targz(output_filename, source_dir):
    """
    一次性打包目录为tar.gz
    :param output_filename: 压缩文件名
    :param source_dir: 需要打包的目录
    :return: bool
    """

    try:
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        print("打包成功！")
        return True, output_filename
    except Exception as e:
        print("打包失败 ：{}".format(e))
        return False, output_filename


class QuicktronSSH():

    def __init__(self, hostname, port=2223):
        self.hostname = hostname
        self.port = port
        self.ssh = paramiko.SSHClient()
        # 把要连接的机器添加到known_hosts文件中
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            hostname=self.hostname,
            port=self.port,
            username="quicktron",
            password="quicktron",
            timeout=5,
        )
        self.sender = self.ssh.invoke_shell()
        self.sudo_root()
        self.set_trans()

    def set_trans(self):
        """生成ftp对象"""
        self.trans = paramiko.Transport((self.hostname, self.port))
        self.trans.connect(username="quicktron", password="quicktron")
        self.sftp = paramiko.SFTPClient.from_transport(self.trans)

    def put_file(self, local_file, target_file):
        """上传的文件权限为quicktron"""
        self.sftp.put(local_file, target_file)

    def exe_cmd(self, cmd, t=1):
        """执行命令"""
        self.sender.send(cmd)
        self.sender.send("\n")
        time.sleep(t)
        resp = self.sender.recv(9999).decode("utf8")
        return resp

    def sudo_root(self):
        # 切换root账号
        resp = self.exe_cmd("sudo su", t=0.5)
        if resp.endswith(u"password for quicktron: "):
            resp = self.exe_cmd("quicktron")
        else:
            print("获取root权限失败")

    def monitor_cmd(self, cmd, flag, t=1):
        """监控指令是否完成"""
        self.sender.send(cmd)
        self.sender.send("\n")
        time.sleep(t)
        resp = self.sender.recv(9999).decode("utf8")
        while True:
            if flag not in resp:
                resp = self.sender.recv(9999).decode("utf8")
                time.sleep(0.5)
                print("监控中:{}".format(resp))
            else:
                print("监控结束")
                break


if __name__ == '__main__':

    # 源代码src目录位置  注意相对路径还是绝对路径
    source_filename = "./src"
    # 生成的源代码压缩包位置
    output_filename = "./src.tar.gz"
    # 部署的机器人ip
    root_ip = "172.31.242.34"

    # 生成源码src压缩包
    flag, local_file = make_targz(output_filename, source_filename)
    if not flag:
        print("压缩失败")
        exit(0)

    q = QuicktronSSH(root_ip, 2223)
    # 删除旧的源码文件
    print("删除旧的源码文件")
    # print(q.exe_cmd("rm -f /tmp/src.tar.gz"))
    q.exe_cmd("rm -f /tmp/src.tar.gz")
    # 上传新源码文件
    print("上传新源码文件")
    # q.put_file("src.tar.gz", "/tmp/src.tar.gz")
    q.put_file(output_filename, "/tmp/src.tar.gz")
    # 移动到挂载目录下
    print("移动到挂载目录下")
    # print(q.exe_cmd("mv /tmp/src.tar.gz /mnt/home/quicktron/data/upper_computer_data/"))
    q.exe_cmd("mv /tmp/src.tar.gz /mnt/home/quicktron/data/upper_computer_data/")
    # print(q.exe_cmd("chown root.root /mnt/home/quicktron/data/upper_computer_data/src.tar.gz"))
    print("修改权限")
    q.exe_cmd("chown root.root /mnt/home/quicktron/data/upper_computer_data/src.tar.gz")
    # 容器内部替换src文件夹
    print("容器内部替换src文件夹")
    # print(q.exe_cmd("docker exec -i upper_computer rm -rf /upper_computer/src"))
    # print(q.exe_cmd("docker exec -i upper_computer tar -xvzf /data/src.tar.gz -C /upper_computer"), 5)
    # print(q.exe_cmd("docker exec -i upper_computer chown root.root -R /upper_computer/src"))

    q.exe_cmd("docker exec -i upper_computer rm -rf /upper_computer/src")
    q.exe_cmd("docker exec -i upper_computer tar -xvzf /data/src.tar.gz -C /upper_computer", 10)
    q.exe_cmd("docker exec -i upper_computer chown root.root -R /upper_computer/src")

    shell_text = """cat << EOF > /mnt/home/quicktron/data/upper_computer_data/start.sh
#!/bin/bash
cd /upper_computer
ps -ax|grep 'python'|awk '{print $1}'|xargs kill -9
rm -rf install
source /opt/ros/melodic/setup.bash && catkin_make install
cp -r /upper_computer/src/upper_computer_ui/script/upper_computer_ui/dist  /upper_computer/install/lib/python2.7/dist-packages/upper_computer_ui
bash start.sh
EOF"""
    # print(q.exe_cmd(shell_text))
    # print(q.exe_cmd("docker exec -i upper_computer chmod +x /data/start.sh"))
    # print(q.monitor_cmd("docker exec -i upper_computer bash /data/start.sh", "netlog start"))

    print("生成临时启动脚本")
    q.exe_cmd(shell_text)
    print("修改脚本权限")
    q.exe_cmd("docker exec -i upper_computer chmod +x /data/start.sh")
    print("重新编译启动")
    q.monitor_cmd("docker exec -i upper_computer bash /data/start.sh", "netlog start")
    print("本地部署完成")


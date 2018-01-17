#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import subprocess
import json
import const
import pyev
from log import log
from host import host
from config import config
from bson.objectid import ObjectId
from cloud_com import cloud_com
from docker_mov import docker_mov
from docker_upgrade import docker_upgrade

class docker_com(cloud_com, docker_mov, docker_upgrade):

    def __init__(self, server):
        #调用父类构造函数
        cloud_com.__init__(self, server.loop)
        docker_mov.__init__(self, server)
        docker_upgrade.__init__(self, server)
        self.command = "docker create --tmpfs /tmp -ti --ipc=host --privileged=true -v %s "%(const.COM_HOST_SOCK_VOLUME)
        self.loop = server.loop
        self.host = host()
        self.child_watcher_timer = pyev.Timer(30, 0, server.loop, self.__child_timer_cb)
        self.child_watcher_timer.start()
        self.config = config()
        self.mongo = server.inner_mongo
        self.pid_to_image = {}
        self.pid_to_name = {}

    def resource_run(self):
        #inner_db连接不上，返回的docker_start_cfg默认为空list不能做全删处理
        ret = self.__load_mongo_cfg()
        if not ret:
            return
        self.__load_old_cfg()
        seg_table = self.get_upgrade_seg_table() + self.get_mov_seg_table()
        for a in self.all:
            if a["name"] in seg_table:
                continue
            if a not in self.old:
                if self.__find_local_image(a["image"]):
                    log.debug("add com:%s"%(a["name"]))
                    self.__update_user_task(a["com_id"], "running", "")
                    self.__start(a)
                else:
                    self.__docker_pull_image(a["name"], a["image"])
        for b in self.old:
            if b["name"] in seg_table:
                continue
            if b not in self.all:
                flag = False
                for c in self.all:
                    if b["name"] == c["name"]:
                        log.debug("stop com:%s"%(b["name"]))
                        self.__stop(b["name"])
                        flag = True
                if flag:
                    continue
                log.debug("delete com:%s"%(b["name"]))
                self.__stop(b["name"])
                self.__rm_data(b["name"])
                self.__update_user_task(b["com_id"], "finish", "success")
        self.__dump_old_cfg()

    def __find_local_image(self, name):
        temp = name.split(":")
        repository = "%s:%s"%(temp[0], temp[1])
        tag = temp[2]
        commands = "docker images | grep {repository_name} | grep {tag_name}".format(repository_name=repository, tag_name=tag)
        log.debug(repr(commands))
        try:
            result = subprocess.check_output(commands, stderr=subprocess.STDOUT, shell=True)
            return True
        except subprocess.CalledProcessError, exc:
            return False

    def __docker_pull_image(self, docker_name, name):
        values = self.pid_to_image.values()
        if name in values:
            return
        commands = "docker pull {image_name}".format(image_name=name)
        log.debug(repr(commands))
        try:
            proc_child = subprocess.Popen(commands, shell=True)
            self.pid_to_image[proc_child.pid] = name
            self.pid_to_name[proc_child.pid] = docker_name
        except Exception:
            log.exception("")

    def __find_docker_cfg(self):
        list = []
        ret = False
        try:
            result = self.mongo.find_one("inner_db", "resource", {"_id":ObjectId(self.config.get_vm_id())})
            if result:
                ret = True
                data = result.get("docker_start_cfg", "")
                try:
                    list = json.loads(data)
                except Exception:
                    log.exception("")
            else:
                log.error("resource of inner_db not exist vm")
        except Exception:
            log.exception("")
        return list, ret

    def __update_user_task(self, com_id, status, desc):
        log.debug("update user task docker_id:%s %s"%(com_id, status))
        try:
            self.mongo.update("task", "user_task",
                            {"docker_id": {"$in": [ObjectId(com_id)]},
                             "status":{"$nin": ["finish", "fail"]}},
                            {
                                "$set": {"status": status, "desc": desc}
                            }
                            )
        except Exception:
            log.exception("")

    def __load_mongo_cfg(self):
        #组件全部配置
        self.all, ret = self.__find_docker_cfg()
        return ret

    def __load_old_cfg(self):
        #组件旧配置
        self.old = []
        try:
            with open(const.DOCKER_INFO_CFG, "r") as f:
                self.old = json.load(f)
        except Exception:
            log.exception("")

    def __dump_old_cfg(self):
        try:
            with open(const.DOCKER_INFO_CFG, "w") as f:
                json.dump(self.all, f)
        except Exception:
            log.exception("")

    def __build_commands(self, data):
        self.name = data.get("name", "")
        self.com_id = data.get("com_id", "")
        self.env = data.get("env", "")
        self.dns = data.get("dns", "")
        self.pipework = data.get("pipework", "")
        self.udp = data.get("udp", "")
        self.tcp = data.get("tcp", "")
        self.net = data.get("net", "")
        self.volumes = data.get("volumes", "")
        self.image = data.get("image", "")
        self.host_before = data.get("host_before", "")
        self.cmd = data.get("cmd", "")

        commands = ""
        if self.name == "":
            log.error("docker name is null")
            return
        commands = self.command + "--name=%s "%(self.name)
        host_ip = self.host.get_ip("eth0")
        center_ip = self.config.get_center_ip()
        if host_ip == "" or center_ip == "":
            log.error("host_ip center_ip is null")
            return
        commands += "-e HOST_IP='%s' -e CENTER_IP='%s' "%(host_ip, center_ip)

        for env in self.env:
            value = env.get("value", "")
            if value != "":
                try:
                    commands += "-e %s "%(value.format(center_ip=host_ip,mac1=self.host.get_mac_str("eth0"),mac2=self.host.get_mac_str("eth1")))
                except Exception:
                    log.exception("")

        if self.dns != "":
            commands += "--dns=%s "%(self.dns.format(center_ip=center_ip,host_ip=host_ip))

        if self.pipework == "":
            if self.net == "":
                self.net = "bridge"
            commands += "--net=%s "%(self.net)

            for udp in self.udp:
                port = udp.get("port", "")
                if port != "":
                    commands += "-p %s/udp "%(port)
            for tcp in self.tcp:
                port = tcp.get("port", "")
                if port != "":
                    commands += "-p %s/tcp "%(port)
        else:
            if self.net == "":
                self.net = "none"
            commands += "--net=%s "%(self.net)

        for vol in self.volumes:
            path = vol.get("path", "")
            if path != "":
                commands += "-v %s "%(path.format(cont_name=self.name))
        if self.image == "" or self.cmd == "":
            log.error("image cmd is null")
            return
        commands += "%s %s"%(self.image, self.cmd)

        return commands

    def __build_host_before(self):
        if self.host_before == "":
            return

        file_content = self.host_before.format(cont_name=self.name)
        try:
            with open(const.PATH_HOST_BEFORE, 'w') as f:
                f.write(file_content)
        except Exception:
            log.exception("")

        commands = "chmod 777 %s"%(const.PATH_HOST_BEFORE)
        log.debug(repr(commands))
        self.__run_cmd(commands)

    def __run_cmd(self, cmd):
        try:
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            return True
        except subprocess.CalledProcessError, exc:
            log.error(exc.output)
            return False

    def __start(self, data):
        commands = self.__build_commands(data)
        log.debug(repr(commands))
        try:
            result = subprocess.check_output(commands, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError, exc:
            log.error(exc.output)
            self.__update_user_task(self.com_id, "fail", exc.output)
            return False

        #运行容器前执行host before脚本
        if self.host_before != "":
            self.__build_host_before()
            commands = "bash {0}".format(const.PATH_HOST_BEFORE)
            log.debug(repr(commands))
            self.__run_cmd(commands)

        commands = "docker start {cont_name}".format(cont_name=self.name)
        log.debug(repr(commands))
        try:
            result = subprocess.check_output(commands, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError, exc:
            log.error(exc.output)
            self.__update_user_task(self.com_id, "fail", exc.output)
            return False

        if self.pipework != "":
            commands = "pipework br0 -i eth0 {cont_name} {pipework}".format(cont_name=self.name,pipework=self.pipework)
            log.debug(repr(commands))
            self.__run_cmd(commands)
        self.__update_user_task(self.com_id, "finish", "success")
        return True

    def start(self, name):
        self.__load_mongo_cfg()
        for a in self.all:
            if a["name"] == name:
                if self.__find_local_image(a["image"]):
                    self.__start(a)
                else:
                    self.__docker_pull_image(a["name"], a["image"])

    def stop(self, name):
        self.__stop(name)
        self.__rm_data(name)

    def __stop(self, name):
        commands = "docker rm -f {cont_name}".format(cont_name=name)
        log.debug(repr(commands))
        self.__run_cmd(commands)

    def __rm_data(self, name):
        commands = "rm -rf /wns/data/{cont_name}".format(cont_name=name)
        log.debug(repr(commands))
        self.__run_cmd(commands)

    def __child_timer_cb(self, watcher, revents):
        self.upgrade_check()
        self.mov_check()
        self.__child_check()
        self.child_watcher_timer.set(30, 0)
        self.child_watcher_timer.start()

    def __child_check(self):
        keys = self.pid_to_image.keys()
        for key in keys:
            try:
                (pid, ret) = os.waitpid(key, os.WNOHANG)
                #进程异常退出ret!=0
                if ret:
                    log.error("child_proc:%d exit ret=%d"%(pid, ret))
                    del self.pid_to_image[key]
                    del self.pid_to_name[key]
            except Exception:
                log.exception("")
                self.start(self.pid_to_name[key])
                del self.pid_to_image[key]
                del self.pid_to_name[key]
        self.resource_run()

    def __timer_cb(self, watcher, revents):
        self.__com_restart()
        self.watcher_timer.set(30, 0)
        self.watcher_timer.start()

    def resource_restart_timer(self):
        self.__com_restart()
        self.watcher_timer = pyev.Timer(30, 0, self.loop, self.__timer_cb)
        self.watcher_timer.start()

    def __com_restart(self):
        self.__load_old_cfg()
        seg_table = self.get_upgrade_seg_table() + self.get_mov_seg_table()
        for a in self.old:
            if a["name"] in seg_table:
                continue
            commands = "docker exec -i {cont_name} ls".format(cont_name=a["name"])
            if not self.__run_cmd(commands):
                commands = "docker restart {cont_name}".format(cont_name=a["name"])
                log.debug(repr(commands))
                if self.__run_cmd(commands):
                    if a.get("pipework", "") != "":
                        commands = "pipework br0 -i eth0 {cont_name} {pipework}".format(cont_name=a["name"], pipework=a["pipework"])
                        log.debug(repr(commands))
                        self.__run_cmd(commands)
                else:
                    self.__stop(a["name"])
                    if self.__find_local_image(a["image"]):
                        log.debug("add com:%s" % (a["name"]))
                        self.__update_user_task(a["com_id"], "running", "")
                        self.__start(a)
                    else:
                        self.__docker_pull_image(a["name"], a["image"])
        commands = "docker ps -a --format \"{{.Names}}\""
        try:
            result = subprocess.check_output(commands, stderr=subprocess.STDOUT, shell=True)
            temp = result.splitlines(False)
            temp.remove("com_host")
            temp_name = []
            for a in self.old:
                temp_name.append(a["name"])
            for b in temp:
                if (b not in temp_name) and (b not in seg_table):
                    if b[:6] == "child_":
                        continue
                    log.debug("delete com:%s"%(b))
                    self.__stop(b)
                    self.__rm_data(b)
                    for c in self.old:
                        if b == c["name"]:
                            self.__update_user_task(c["com_id"], "finish", "success")
        except subprocess.CalledProcessError, exc:
            log.error(exc.output)

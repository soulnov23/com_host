#!/usr/bin/python
# -*- coding: UTF-8 -*-
import subprocess
import json
import const
import pyev
from log import log
from host import host
from config import config

class cloud_com():

    def __init__(self, loop):
        self.command = "docker create --tmpfs /tmp -ti --ipc=host --privileged=true "
        self.loop = loop
        self.host = host()
        self.config = config()
        self.sdw_ver = {}

    def cloud_run(self):
        self.__load_center_cfg()
        self.__load_version()
        for a in self.center:
            self.__start(a)

    def __load_center_cfg(self):
        self.center = []
        try:
            with open(const.CENTER_INFO_CFG, "r") as f:
                self.center = json.load(f)
        except Exception:
            log.exception("")

    def __load_version(self):
        try:
            with open(const.VERSION_CFG, "r") as f:
                while True:
                    lines = f.readline()
                    if not lines:
                        break
                    vers = lines.split("=")
                    self.sdw_ver[vers[0]] = vers[1].rstrip('\n')
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
        self.image = data.get("image", "").format(sdw_center=self.sdw_ver.get("sdw_center", ""), \
                                                sdw_svn=self.sdw_ver.get("sdw_svn", ""),\
                                                sdw_web=self.sdw_ver.get("sdw_web", ""), \
                                                sdw_db=self.sdw_ver.get("sdw_db", ""))
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
                commands += "-e %s "%(value)

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
        self.__run_cmd(commands)

        #运行容器前执行host before脚本
        if self.host_before != "":
            self.__build_host_before()
            commands = "bash {0}".format(const.PATH_HOST_BEFORE)
            log.debug(repr(commands))
            self.__run_cmd(commands)

        commands = "docker start {cont_name}".format(cont_name=self.name)
        log.debug(repr(commands))
        self.__run_cmd(commands)

        if self.pipework != "":
            commands = "pipework br0 -i eth0 {cont_name} {pipework}".format(cont_name=self.name,pipework=self.pipework)
            log.debug(repr(commands))
            self.__run_cmd(commands)

    def __stop(self, name):
        commands = "docker rm -f {cont_name}".format(cont_name=name)
        log.debug(repr(commands))
        self.__run_cmd(commands)

    def __rm_data(self, name):
        commands = "rm -rf /wns/data/{cont_name}".format(cont_name=name)
        log.debug(repr(commands))
        self.__run_cmd(commands)

    def __timer_cb(self, watcher, revents):
        self.__com_restart()
        self.watcher_timer.set(30, 0)
        self.watcher_timer.start()

    def cloud_restart_timer(self):
        self.__com_restart()
        self.watcher_timer = pyev.Timer(30, 0, self.loop, self.__timer_cb)
        self.watcher_timer.start()

    def __com_restart(self):
        if self.host.is_center():
            self.__load_center_cfg()
            self.__load_version()
            for a in self.center:
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
                        self.__start(a)
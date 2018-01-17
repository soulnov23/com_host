#!/usr/bin/python
# -*- coding: UTF-8 -*-

import subprocess
import json
import const
import pyev
from log import log

class com_host_update:

    def __init__(self, server):
        self.server = server
        self.watcher_timer = pyev.Timer(60, 0, self.server.loop, self.__timer_cb)

    def __timer_cb(self, watcher, revents):
        self.__com_host_update()
        self.watcher_timer.set(60, 0)
        self.watcher_timer.start()

    def update_timer(self):
        self.__com_host_update()
        self.watcher_timer.start()

    def __get_remote_image_tag(self):
        command = "bash %s search_image com_host"%(const.SDREGISTRY_SHELL_PATH)
        #log.debug(repr(command))
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError, exc:
            log.error(exc.output)
            result = ""
        return result

    def __get_local_image_tag(self):
        command = "docker inspect --format='{{.Config.Image}}' com_host"
        #log.debug(repr(command))
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError, exc:
            log.error(exc.output)
            result = ""
        return result

    def __com_host_update(self):
        data = self.__get_remote_image_tag()
        try:
            image_info = json.loads(data)
        except Exception:
            log.exception("")
            return
        image_name = image_info.get("name", "")
        #{"errors":}镜像不存在情况
        if image_name == "":
            log.error("image not exist")
        else:
            image_tag = image_info.get("tags", "")
            #{"name":"com_host","tags":null}镜像已删除情况
            if image_tag == None:
                log.error("image is deleted")
            else:
                if type(image_tag) is list:
                    tag = image_tag[0]
                    for tag_temp in image_tag:
                        if int(tag[4:]) < int(tag_temp[4:]):
                            tag = tag_temp
                else:
                    tag = image_tag
                remote = "sdwan.io:5000/%s:%s"%(image_name, tag)
                local = self.__get_local_image_tag().replace("\n", "")
                if remote != local:
                    log.debug("update com_host")
                    log.debug(repr(remote))
                    log.debug(repr(local))
                    command = "bash %s update %s"%(const.COM_HOST_SHELL_PATH, remote)
                    log.debug(command)
                    try:
                        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                    except subprocess.CalledProcessError, exc:
                        log.error(exc.output)
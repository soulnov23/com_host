#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import os
import subprocess
import const
import time
import datetime
import pyev
import json
from log import log
from bson.objectid import ObjectId
from config import config

class docker_upgrade:

    def __init__(self, server):
        self.__inner_mongo = server.inner_mongo
        self.__rsc_mongo = server.rsc_mongo
        self.__config = config()
        self.__seg_table = []
        self.__pid_to_name = {}
        self.__pid_to_task = {}

    def start(self, name):
        pass

    def stop(self, name):
        pass

    def __update_user_upgrade_task(self, _id, status, desc):
        log.debug("update user upgrade task _id:%s %s"%(_id.__str__(), status))
        try:
            self.__inner_mongo.update("task", "user_upgrade_task",
                                      {"_id": _id,
                                       "status": {"$nin": ["finish", "fail"]}},
                                      {
                                          "$set": {"status": status, "desc": desc}
                                      }
                                      )
        except Exception:
            log.exception("")

    def __find_user_upgrade_task(self):
        result = []
        try:
            result = self.__inner_mongo.find("task", "user_upgrade_task",
                    {"resource_id":ObjectId(self.__config.get_vm_id()),
                     "status": {"$nin": ["finish", "fail"]}})
        except Exception:
            log.exception("")
        return result

    def upgrade_check(self):
        keys = self.__pid_to_task.keys()
        for key in keys:
            try:
                (pid, ret) = os.waitpid(key, os.WNOHANG)
                #进程异常退出ret!=0
                if ret:
                    log.error("child_proc:%d exit ret=%d" % (pid, ret))
                    self.__rollback(self.__pid_to_task[key])
                    (old_name, new_name) = self.__pid_to_name[key]
                    self.__delete_from_seg_table(old_name)
                    self.__delete_from_seg_table(new_name)
                    del self.__pid_to_task[key]
                    del self.__pid_to_name[key]
            except Exception:
                log.exception("")
                self.__update_user_upgrade_task(self.__pid_to_task[key], "data_ok", "")
                del self.__pid_to_task[key]
                del self.__pid_to_name[key]
        self.upgrade()

    def __rollback(self, task):
        try:
            result = self.__inner_mongo.find_one("task", "user_upgrade_task", {"_id": task})
            if result:
                old_name = result["old_name"]
                old_version = result["old_version"]
                docker_id = result["docker_id"]
                type = result["rsc_type"]
                if type == "sc":
                    self.__rsc_mongo.update("default", "user",
                                            {"docker_id": docker_id},
                                            {
                                                "$set": {"sc_name": old_name, "version": old_version}
                                            }
                                            )
                elif type == "branch":
                    self.__rsc_mongo.update("default", "branch_config",
                                            {"docker_id": docker_id},
                                            {
                                                "$set": {"brh_name": old_name, "version": old_version}
                                            }
                                            )
                temp = self.__inner_mongo.find_one("inner_db", "resource", {"_id": ObjectId(self.__config.get_vm_id())})
                if temp:
                    data = json.loads(temp["docker_start_cfg"])
                    for docker in data:
                        if docker["com_id"] == docker_id:
                            docker["name"] = old_name
                            docker["image"] = old_version
                    data_temp = json.dumps(data)
                    self.__inner_mongo.update("inner_db", "resource",
                                            {"_id": ObjectId(self.__config.get_vm_id())},
                                            {
                                                "$set": {"docker_start_cfg": data_temp}
                                            }
                                            )
                self.__update_user_upgrade_task(task, "fail", "rsync return -1")
        except Exception:
            log.exception("")

    def upgrade(self):
        try:
            result = self.__find_user_upgrade_task()
            for task in result:
                old_name = task["old_name"]
                new_name = task["new_name"]
                self.__insert_into_seg_table(old_name)
                self.__insert_into_seg_table(new_name)
                if task["status"] == "start":
                    values = self.__pid_to_task.values()
                    if task["_id"] in values:
                        continue
                    commands = "docker stop -t 1 {cont_name}".format(cont_name=old_name)
                    log.debug(repr(commands))
                    try:
                        result = subprocess.check_output(commands, stderr=subprocess.STDOUT, shell=True)
                    except subprocess.CalledProcessError, exc:
                        log.error(exc.output)
                    rsync_cmd = "rsync -a /wns/data/%s/ /wns/data/%s"%(old_name, new_name)
                    log.debug(repr(rsync_cmd))
                    try:
                        proc_child = subprocess.Popen(rsync_cmd, shell=True)
                        self.__pid_to_name[proc_child.pid] = (old_name, new_name)
                        self.__pid_to_task[proc_child.pid] = task["_id"]
                    except Exception:
                        log.exception("")
                elif task["status"] == "data_ok":
                    self.__delete_from_seg_table(new_name)
                    self.start(new_name)
                    commands = "docker ps | grep {cont_name}".format(cont_name=new_name)
                    log.debug(repr(commands))
                    try:
                        result = subprocess.check_output(commands, stderr=subprocess.STDOUT, shell=True)
                        self.__update_user_upgrade_task(task["_id"], "docker_ok", "")
                    except subprocess.CalledProcessError, exc:
                        log.error(exc.output)
                elif task["status"] == "docker_ok":
                    self.__delete_from_seg_table(new_name)
                    self.__delete_from_seg_table(old_name)
                    self.stop(old_name)
                    commands = "docker ps | grep {cont_name}".format(cont_name=old_name)
                    log.debug(repr(commands))
                    try:
                        result = subprocess.check_output(commands, stderr=subprocess.STDOUT, shell=True)
                    except subprocess.CalledProcessError, exc:
                        log.error(exc.output)
                        self.__update_user_upgrade_task(task["_id"], "finish", "success")
                elif task["status"] == "prepare":
                    log.error("cloud_srv not modify user upgrade status")
        except Exception:
            log.exception("")

    def __insert_into_seg_table(self, docker_name):
        '''插入到隔离表'''
        if docker_name not in self.__seg_table:
            self.__seg_table.append(docker_name)

    def __delete_from_seg_table(self, docker_name):
        '''从隔离表删除'''
        if docker_name in self.__seg_table:
            self.__seg_table.remove(docker_name)

    def get_upgrade_seg_table(self):
        return self.__seg_table

#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import os
import subprocess
import const
import time
import pyev
import json
from log import log
from bson.objectid import ObjectId
from config import config

class docker_mov:

    def __init__(self, server):
        self.__loop = server.loop
        self.__inner_db = server.inner_mongo
        self.__rsc_db = server.rsc_mongo
        self.__mqtt = server.mqtt
        self.__config = config()
        self.__pid_to_name = {}
        self.__pid_to_task = {}
        self.__seg_table = []

    def start(self, name):
        pass

    def stop(self, name):
        pass

    def __update_user_mov_task(self, _id, status, desc):
        log.debug("update user mov task _id:%s %s"%(_id.__str__(), status))
        try:
            self.__inner_db.update("task", "user_mov_task",
                            {"_id": _id,
                             "mov_status":{"$nin": ["finish", "fail"]}},
                            {
                                "$set": {"mov_status": status, "desc": desc}
                            }
                            )
        except Exception:
            log.exception("")

    def __publish_data_ok(self, _id):
        try:
            result = self.__inner_db.find_one("task", "user_mov_task", {"_id": _id})
            if result:
                dst_vm_id = result["dst_rsc"]
                topic = "/cloud/com_host/%s"%(dst_vm_id.__str__())
                self.__mqtt.publish(topic, "")
        except Exception:
            log.exception("")

    def __publish_docker_ok(self, _id):
        try:
            result = self.__inner_db.find_one("task", "user_mov_task", {"_id": _id})
            if result:
                src_vm_id = result["src_rsc"]
                topic = "/cloud/com_host/%s"%(src_vm_id.__str__())
                self.__mqtt.publish(topic, "")
        except Exception:
            log.exception("")

    def mov_send_task(self):
        vm_id = self.__config.get_vm_id()
        query = {"src_rsc": ObjectId(vm_id),
                 "mov_status": {"$nin": ["finish", "fail"]}}
        ret = []
        try:
            ret = self.__inner_db.find("task", "user_mov_task", query)
            if ret:
                values = self.__pid_to_task.values()
                for task in ret:
                    self.__insert_into_seg_table(task["docker_name"])
                    if task["mov_status"] == "start":
                        if task["_id"] in values:
                            continue
                        commands = "docker stop -t 1 {cont_name}".format(cont_name=task["docker_name"])
                        log.debug(repr(commands))
                        try:
                            result = subprocess.check_output(commands, stderr=subprocess.STDOUT, shell=True)
                        except subprocess.CalledProcessError, exc:
                            log.error(exc.output)
                        rsync_cmd = "/wns/shell/rsync.sh %s %d %s %s %s" % ( \
                            task["dst_ip"], task["dst_port"], "root", \
                            "10g", task["docker_name"])
                        log.debug(rsync_cmd)
                        try:
                            proc_child = subprocess.Popen(rsync_cmd, shell=True, stdout=subprocess.PIPE)
                            self.__pid_to_task[proc_child.pid] = task["_id"]
                            self.__pid_to_name[proc_child.pid] = task["docker_name"]
                        except Exception:
                            log.exception("")
                    elif task["mov_status"] == "docker_ok":
                        self.__delete_from_seg_table(task["docker_name"])
                        self.stop(task["docker_name"])
                        commands = "docker ps | grep {cont_name}".format(cont_name=task["docker_name"])
                        log.debug(repr(commands))
                        try:
                            result = subprocess.check_output(commands, stderr=subprocess.STDOUT, shell=True)
                        except subprocess.CalledProcessError, exc:
                            log.error(exc.output)
                            self.__update_user_mov_task(task["_id"], "finish", "success")
                    elif task["mov_status"] == "prepare":
                        log.error("cloud_srv not modify user mov status")
        except Exception:
            log.exception("")

    def mov_recv_task(self):
        vm_id = self.__config.get_vm_id()
        query = {"dst_rsc": ObjectId(vm_id),
                 "mov_status": {"$nin": ["finish", "fail"]}}
        ret = []
        try:
            ret = self.__inner_db.find("task", "user_mov_task", query)
            if ret:
                for task in ret:
                    self.__insert_into_seg_table(task["docker_name"])
                    if task["mov_status"] == "data_ok":
                        self.__delete_from_seg_table(task["docker_name"])
                        self.start(task["docker_name"])
                        commands = "docker ps | grep {cont_name}".format(cont_name=task["docker_name"])
                        log.debug(repr(commands))
                        try:
                            result = subprocess.check_output(commands, stderr=subprocess.STDOUT, shell=True)
                            self.__update_user_mov_task(task["_id"], "docker_ok", "")
                            self.__publish_docker_ok(task["_id"])
                        except subprocess.CalledProcessError, exc:
                            log.error(exc.output)
                    elif task["mov_status"] == "docker_ok":
                        self.__delete_from_seg_table(task["docker_name"])
                    elif task["mov_status"] == "prepare":
                        log.error("cloud_srv not modify user mov status")
        except Exception:
            log.exception("")

    def mov_check(self):
        keys = self.__pid_to_task.keys()
        for key in keys:
            try:
                (pid, ret) = os.waitpid(key, os.WNOHANG)
                #进程异常退出ret!=0
                if ret:
                    log.error("child_proc:%d exit ret=%d"%(pid, ret))
                    self.__rollback(self.__pid_to_task[key])
                    name = self.__pid_to_name[key]
                    self.__delete_from_seg_table(name)
                    del self.__pid_to_task[key]
                    del self.__pid_to_name[key]
            except Exception:
                log.exception("")
                self.__update_user_mov_task(self.__pid_to_task[key], "data_ok", "success")
                self.__publish_data_ok(self.__pid_to_task[key])
                del self.__pid_to_task[key]
                del self.__pid_to_name[key]
        self.mov_send_task()
        self.mov_recv_task()

    def __rollback(self, task):
        try:
            result = self.__inner_db.find_one("task", "user_mov_task", {"_id": task})
            if result:
                src_vm_id = result["src_rsc"]
                dst_vm_id = result["dst_rsc"]
                docker_id = result["docker_id"]
                type = result["rsc_type"]
                if type == "sc":
                    self.__rsc_db.update("default", "user",
                                            {"docker_id": docker_id},
                                            {
                                                "$set": {"resource_id": src_vm_id}
                                            }
                                            )
                elif type == "branch":
                    self.__rsc_db.update("default", "branch_config",
                                            {"docker_id": docker_id},
                                            {
                                                "$set": {"resource_id": src_vm_id}
                                            }
                                            )
                dst_temp = self.__inner_db.find_one("inner_db", "resource", {"_id": dst_vm_id})
                if dst_temp:
                    log.error("inner_db resource not exist vm_id:%s"%(dst_vm_id.__str__()))
                    return
                src_temp = self.__inner_db.find_one("inner_db", "resource", {"_id": src_vm_id})
                if src_temp:
                    log.error("inner_db resource not exist vm_id:%s"%(src_vm_id.__str__()))
                    return
                src_data = json.loads(dst_temp["docker_start_cfg"])
                dst_data = json.loads(dst_temp["docker_start_cfg"])
                for docker in dst_data:
                    if docker["com_id"] == docker_id:
                        dst_data.remove(docker)
                        src_data.append(docker)
                        break
                src_data_temp = json.dumps(src_data)
                dst_data_temp = json.dumps(dst_data)
                self.__inner_db.update("inner_db", "resource",
                                        {"_id": src_vm_id},
                                        {
                                            "$set": {"docker_start_cfg": src_data_temp}
                                        }
                                        )
                self.__inner_db.update("inner_db", "resource",
                                       {"_id": dst_vm_id},
                                       {
                                           "$set": {"docker_start_cfg": dst_data_temp}
                                       }
                                       )
                self.__update_user_mov_task(task, "fail", "rsync return -1")
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

    def get_mov_seg_table(self):
        '''返回隔离表'''
        return self.__seg_table
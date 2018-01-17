#!/usr/bin/python
# -*- coding: UTF-8 -*-
import psutil
import time
import pyev
import subprocess
import json
from config import config
from log import log
from bson.objectid import ObjectId

class status:

    def __init__(self, server):
        self.inner_mongo = server.inner_mongo
        self.mongo = server.outside_mongo
        self.mongo_timer = pyev.Timer(60, 0, server.loop, self.__mongo_timer_cb)
        self.vm_timer = pyev.Timer(60, 0, server.loop, self.__vm_timer_cb)
        self.config = config()

    def __mongo_timer_cb(self, watcher, revents):
        self.__update_mongo_status()
        self.mongo_timer.set(60, 0)
        self.mongo_timer.start()

    def mongo_status_timer(self):
        try:
            result = self.inner_mongo.find_one("inner_db", "resource", {"_id":ObjectId(self.config.get_vm_id())})
        except Exception:
            log.exception("")
        if result:
            name = result.get("resource_name", "")
            if name == "sdwan_mongo_srv":
                log.debug("this is mongo resource")
                self.__update_mongo_status()
                self.mongo_timer.start()
        else:
            log.error("resource of inner_db not exist vm")

    def __update_mongo_status(self):
        mongo_dict = {}
        now = time.time()
        mongo_dict["time"] = int(now - now%60)
        command = "iostat -d vda -x | grep vda | awk '{print $6}{print $7}{print $NF}'"
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            list = result.splitlines(False)
            mongo_dict["rsec"] = float(list[0])
            mongo_dict["wsec"] = float(list[1])
            mongo_dict["util"] = float(list[2])
        except subprocess.CalledProcessError, exc:
            mongo_dict["rsec"] = float(0)
            mongo_dict["wsec"] = float(0)
            mongo_dict["util"] = float(0)
            log.error(exc.output)
        try:
            #log.debug("insert mongo status:%s"%(mongo_dict))
            self.mongo.insert_one("state_db", "mongo_io_minute_tbl", mongo_dict)
        except Exception:
            log.exception("")

    def __vm_timer_cb(self, watcher, revents):
        self.__update_vm_status()
        self.vm_timer.set(60, 0)
        self.vm_timer.start()

    def vm_status_timer(self):
        self.__update_vm_status()
        self.vm_timer.start()

    def __update_vm_status(self):
        vm_dict = {}
        vm_dict["vm_id"] = self.config.get_vm_id()
        vm_dict["cpu"] = psutil.cpu_times_percent(interval=1, percpu=False).user
        vm_dict["memory"] = psutil.virtual_memory().percent
        vm_dict["disk"] = psutil.disk_usage("/").percent
        command = "iostat -d vda -x | grep vda | awk '{print $NF}'"
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            vm_dict["io"] = float(result)
        except subprocess.CalledProcessError, exc:
            vm_dict["io"] = float(0)
            log.error(exc.output)
        try:
            result = self.mongo.find_one("state_db", "vm_status", {"vm_id":vm_dict["vm_id"]})
            if result:
                #log.debug("update vm_status:%s"%(vm_dict))
                self.mongo.update("state_db", "vm_status",
                    {"vm_id":vm_dict["vm_id"]},
                    {
                        "$set":vm_dict
                    }
                )
            else:
                #log.debug("insert vm_status:%s" % (vm_dict))
                self.mongo.insert_one("state_db", "vm_status", vm_dict)
        except Exception:
            log.exception("")
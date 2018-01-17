#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import const
from log import log

class config:

    def get_vm_id(self):
        vm_id = ""
        try:
            with open(const.COM_HOST_JSON_PATH, "r") as f:
                data = json.load(f)
                vm_id = data.get("vm_id", "")
        except Exception:
            log.exception("")
        return vm_id

    def set_vm_id(self, vm_id):
        center_ip = ""
        try:
            with open(const.COM_HOST_JSON_PATH, "r") as f:
                data = json.load(f)
                center_ip = data.get("center_ip", "")
        except Exception:
            log.exception("")
        
        try:
            file = open(const.COM_HOST_JSON_PATH, "w")
            data_temp = {}
            data_temp["center_ip"] = center_ip
            data_temp["vm_id"] = vm_id
            json.dump(data_temp, file)
        except Exception:
            log.exception("")
        else:
            file.close()

    def get_center_ip(self):
        center_ip = ""
        try:
            with open(const.COM_HOST_JSON_PATH, "r") as f:
                data = json.load(f)
                center_ip = data.get("center_ip", "")
        except Exception:
            log.exception("")
        return center_ip

    def set_center_ip(self, ip):
        vm_id = ""
        try:
            with open(const.COM_HOST_JSON_PATH, "r") as f:
                data = json.load(f)
                vm_id = data.get("vm_id", "")
        except Exception:
            log.exception("")
        
        try:
            file = open(const.COM_HOST_JSON_PATH, "w")
            data_temp = {}
            data_temp["center_ip"] = ip
            data_temp["vm_id"] = vm_id
            json.dump(data_temp, file)
        except Exception:
            log.exception("")
        else:
            file.close()
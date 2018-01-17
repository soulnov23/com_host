#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import socket
import fcntl
import struct
import subprocess
import binascii
import json
import psutil
import const
from config import config
from log import log

class host:

    def __init__(self):
        self.config = config()

    def is_center(self):
        ret = False
        try:
            with open("/etc/hwinfo", "r") as f:
                lines = f.readlines()
                for line in lines:
                    if line == "product=center\n":
                        ret = True
                        break
        except Exception:
            log.exception("")
        return ret

    def get_mac(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            mac = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
            mac = "".join(['%02x' % ord(char) for char in mac[18:24]])
            mac = binascii.unhexlify(mac)
        except Exception:
            log.exception("")
            mac = ""
        s.close()
        return mac

    def get_mac_str(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            mac = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
            mac = "".join(['%02x' % ord(char) for char in mac[18:24]])
            mac = mac[:2] + ":" + mac[2:4]+ ":" + mac[4:6]+ ":" + mac[6:8]+ ":" + mac[8:10]+ ":" + mac[10:]
        except Exception:
            log.exception("")
            mac = ""
        s.close()
        return mac

    def get_ip(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            addr = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))
            addr = socket.inet_ntoa(addr[20:24])
        except Exception:
            log.exception("")
            addr = ""
        s.close()
        return addr

    def set_ip(self, ip, mask, gateway):
        command = "bash %s set_ip %s %s %s"%(const.COM_HOST_SHELL_PATH, ip, mask, gateway)
        log.debug(repr(command))
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError, exc:
            log.error(exc.output)

    def set_dns(self, dns):
        command = "bash %s set_dns %s"%(const.COM_HOST_SHELL_PATH, dns)
        log.debug(repr(command))
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError, exc:
            log.error(exc.output)

    def clean_image(self):
        command = "bash %s clean"%(const.COM_HOST_SHELL_PATH)
        log.debug(repr(command))
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            log.debug(result)
        except subprocess.CalledProcessError, exc:
            log.error(exc.output)

    def get_info(self, ifname):
        data = {}
        data["vm_id"] = self.config.get_vm_id()
        data["ip"] = self.get_ip(ifname)
        data["cpu_count"] = psutil.cpu_count(logical=False)
        data["mem_size"] = psutil.virtual_memory().total/1024/1024
        data["disk_size"] = psutil.disk_usage('/').total/1024/1024
        try:
            data_temp = json.dumps(data)
        except Exception:
            log.exception("")
            data_temp = ""
        return data_temp
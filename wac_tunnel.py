#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import os
import pyev
import struct
import json
import const
import time
import datetime
from log import log
from config import config
from bson.objectid import ObjectId

"""
struct com_host_msg_hdr
{
    uint32_t magic;0xb9b9
    uint32_t version;
    uint32_t header_len;
    uint32_t data_len;
    uint32_t msg_type;
};
{"docker_id":"","domain_req":""}
data:{"domain_req":"","domain_resp":""}
"""

class wac_tunnel:

    def __init__(self, server):
        self.server = server
        self.mongo = server.inner_mongo
        self.unix_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        path = os.path.split(const.COM_HOST_SOCK_PATH)[0]
        if not os.path.isdir(path):
            os.makedirs(path)
        if os.path.exists(const.COM_HOST_SOCK_PATH):
            os.unlink(const.COM_HOST_SOCK_PATH)
        self.unix_socket.bind(const.COM_HOST_SOCK_PATH)
        self.unix_socket.listen(5)
        self.unix_socket.setblocking(False)
        self.watcher = pyev.Io(self.unix_socket, pyev.EV_READ, self.server.loop, self.__accept_cb)
        self.watcher.start()
        self.watcher_timer = pyev.Timer(30, 0, self.server.loop, self.__timer_cb)
        self.watcher_timer.start()
        self.fd_to_buffer = {}
        self.fd_to_socket = {}
        self.fd_to_wacher = {}
        self.cid_to_time = {}
        self.config = config()

    def __accept_cb(self, watcher, revents):
        if revents & pyev.EV_READ:
            while True:
                try:
                    new_socket, new_addr = self.unix_socket.accept()
                    self.fd_to_socket[new_socket.fileno()] = new_socket
                    log.debug("resolver_socket new accpet")
                    new_socket.setblocking(False)
                    self.fd_to_buffer[new_socket.fileno()] = bytes()
                    new_watcher = pyev.Io(new_socket, pyev.EV_READ, self.server.loop, self.__read_cb)
                    new_watcher.start()
                    self.fd_to_wacher[new_socket.fileno()] = new_watcher
                except socket.error as e:
                    (errno, err_msg) = e
                    if errno == const.EAGAIN:
                        break

    def __read_cb(self, watcher, revents):
        if revents&pyev.EV_READ:
            socket_temp = self.fd_to_socket[watcher.fd]
            while True:
                try:
                    recv_data = socket_temp.recv(1024)
                    #处理正常关闭
                    if recv_data == "":
                        log.debug("close")
                        self.__close(watcher)
                        return
                    else:
                        self.fd_to_buffer[watcher.fd] += recv_data
                #处理异常关闭(EAGAIN,EINTR)
                except socket.error as e:
                    (errno, err_msg) = e
                    if errno == const.EAGAIN:
                        break
                    elif errno == const.EINTR:
                        continue
                    else:
                        log.exception("close")
                        self.__close(watcher)
                        return
            self.__handle_buffer(watcher)

    def __close(self, watcher):
        self.fd_to_socket[watcher.fd].close()
        watcher.stop()
        watcher = None

    def __timer_cb(self, watcher, revents):
        try:
            with open(const.DOCKER_INFO_CFG, "r") as f:
                data = json.load(f)
                com_list = self.cid_to_time.keys()
                temp_list = []
                for docker in data:
                    com_id = docker["com_id"]
                    temp_list.append(com_id)
                    if com_id not in com_list:
                        try:
                            result = self.mongo.find_one("inner_db", "docker", {"_id": ObjectId(com_id)})
                            if result:
                                #log.debug("update docker status:%s offline"%(com_id))
                                self.mongo.update("inner_db", "docker",
                                                  {"_id": ObjectId(com_id)},
                                                  {
                                                      "$set": {"status": "offline"}
                                                  }
                                                  )
                            else:
                                #log.debug("insert docker status:%s offline"%(com_id))
                                self.mongo.insert_one("inner_db", "docker", {"_id": ObjectId(com_id),
                                                    "status": "offline", "rsc_id": ObjectId(self.config.get_vm_id())})
                        except Exception:
                            log.exception("")
                for com in com_list:
                    if com not in temp_list:
                        del self.cid_to_time[com]
        except Exception:
            log.exception("")
        now = time.time()
        for com_id, update_time in self.cid_to_time.items():
            if now - update_time > 90:
                try:
                    result = self.mongo.find_one("inner_db", "docker", {"_id": ObjectId(com_id)})
                    if result:
                        #log.debug("update docker status:%s offline"%(com_id))
                        self.mongo.update("inner_db", "docker",
                                          {"_id": ObjectId(com_id)},
                                          {
                                              "$set": {"status": "offline"}
                                          }
                                          )
                    else:
                        #log.debug("insert docker status:%s offline"%(com_id))
                        self.mongo.insert_one("inner_db", "docker", {"_id": ObjectId(com_id),
                                            "status": "offline", "rsc_id": ObjectId(self.config.get_vm_id())})
                except Exception:
                    log.exception("")
            else:
                try:
                    result = self.mongo.find_one("inner_db", "docker", {"_id": ObjectId(com_id)})
                    if result:
                        #log.debug("update docker status:%s online" % (com_id))
                        self.mongo.update("inner_db", "docker",
                                          {"_id": ObjectId(com_id)},
                                          {
                                              "$set": {"status": "online"}
                                          }
                                          )
                    else:
                        #log.debug("insert docker status:%s online" % (com_id))
                        self.mongo.insert_one("inner_db", "docker", {"_id": ObjectId(com_id),
                                            "status": "online", "rsc_id": ObjectId(self.config.get_vm_id())})
                except Exception:
                    log.exception("")
        self.watcher_timer.set(30, 0)
        self.watcher_timer.start()

    def __handle_buffer(self, watcher):
        buffer = self.fd_to_buffer[watcher.fd]
        while True:
            while len(buffer) > const.UNIX_SOCKET_HEADER_LEN:
                header = struct.unpack("<5I", buffer[:const.UNIX_SOCKET_HEADER_LEN])
                #判断标志位magic是否正确
                if header[0] == const.UNIX_SOCKET_MAGIC:
                    break
                else:
                    buffer = buffer[1:]
            if len(buffer) < const.UNIX_SOCKET_HEADER_LEN:
                break
            data_len = header[3]
            #剩下数据长度不够一个完整包
            if len(buffer) < const.UNIX_SOCKET_HEADER_LEN + data_len:
                break
            data = buffer[const.UNIX_SOCKET_HEADER_LEN:const.UNIX_SOCKET_HEADER_LEN + data_len]
            self.__handle_msg(watcher, header, data)
            #取出完整包，把剩下部分数据重新赋给buffer，相当于删除前面一个完整包
            buffer = buffer[const.UNIX_SOCKET_HEADER_LEN + data_len:]
        self.fd_to_buffer[watcher.fd] = buffer

    def __handle_msg(self, watcher, header, data):
        if header[4] == const.WAC_HEATBEAT:
            self.__handle_heatbeat(watcher, data)
        elif header[4] == const.RESOLVER_REQ:
            self.__handle_resolver(watcher, data)
        elif header[4] == const.APPINIT_CLI_INFO:
            self.__handle_appinit(watcher, data)

    def __handle_heatbeat(self, watcher, data):
        #log.debug("recv:%s"%(data))
        try:
            packet = json.loads(data)
        except Exception:
            log.exception("")
            return
        try:
            com_id = packet["docker_id"]
        except Exception:
            log.exception("")
            return
        now = time.time()
        self.cid_to_time[com_id] = now

    def __handle_resolver(self, watcher, data):
        #log.debug("recv:%s"%(data))
        try:
            packet = json.loads(data)
        except Exception:
            log.exception("")
            return
        try:
            com_id = packet["docker_id"]
            domain = packet["domain_req"]
        except Exception:
            log.exception("")
            return
        rsp_data = {}
        rsp_data["domain_req"] = domain
        rsp_data["domain_resp"] = "178.18.0.3"
        try:
            data_temp = json.dumps(rsp_data)
        except Exception:
            log.exception("")
            data_temp = ""
        data_len = len(data_temp)
        packet_style = "<5I%us"%(data_len)
        packet = struct.pack(packet_style, const.UNIX_SOCKET_MAGIC, const.UNIX_SOCKET_VERSION,
                            const.UNIX_SOCKET_HEADER_LEN, data_len, const.RESOLVER_RSP, data_temp)
        #计算格式后字符串大小
        packet_len = struct.calcsize(packet_style)
        self.__send(watcher, packet, packet_len)

    def __handle_appinit(self, watcher, data):
        log.debug("recv:%s"%(data))
        #appinit_cli info目前不做处理

    def __send(self, watcher, data, len):
        socket_temp = self.fd_to_socket[watcher.fd]
        log.debug(repr(data))
        total_send = 0
        while total_send < len:
            try:
                sent = socket_temp.send(data[total_send:])
                #处理正常关闭
                if sent == 0:
                    log.debug("close")
                    self.__close(watcher)
                    break
                else:
                    total_send = total_send + sent
            #处理异常关闭(EAGAIN,EINTR)
            except socket.error as e:
                (errno, err_msg) = e
                if errno == const.EAGAIN:
                    break
                elif errno == const.EINTR:
                    continue
                else:
                    log.exception("close")
                    self.__close(watcher)
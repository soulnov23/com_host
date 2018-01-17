#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import struct
import json
import const
import pyev
from host import host
from config import config
from log import log

"""
struct ethhdr
{
    unsigned char h_dest[6];
    unsigned char h_source[6];
    uint16_t h_proto;   //0xa990
};
struct packet_header
{
    uint32_t magic;     //MAGIC_WORD 0xa990a990
    uint8_t version; 
    uint8_t hdr_len;
    uint16_t data_len;
    uint8_t msg_type;
    char data[0];
};
"""
class cloud_tunnel:

    def __init__(self, server):
        self.server = server
        self.raw_socket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(const.PROTO))
        self.raw_socket.setblocking(False)
        self.raw_socket.bind(("eth0", 0))
        self.buffer = bytes()
        self.watcher = pyev.Io(self.raw_socket, pyev.EV_READ, self.server.loop, self.__read_cb)
        self.watcher.start()
        self.watcher_timer = pyev.Timer(30, 0, self.server.loop, self.__timer_cb)
        self.config = config()
        self.host = host()

    def __read_cb(self, watcher, revents):
        if revents&pyev.EV_READ:
            while True:
                try:
                    recv_data = self.raw_socket.recv(1024)
                    #处理正常关闭
                    if recv_data == "":
                        log.debug("close raw_socket")
                        self.__close()
                        return
                    else:
                        self.buffer += recv_data
                #处理异常关闭(EAGAIN,EINTR)
                except socket.error as e:
                    (errno, err_msg) = e
                    #log.debug("[%u] %s"%(errno, err_msg))
                    if errno == const.EAGAIN:
                        break
                    elif errno == const.EINTR:
                        continue
                    else:
                        log.exception("close raw_socket")
                        self.__close()
                        return
            self.__handle_buffer()

    def __close(self):
        self.raw_socket.close()
        self.watcher.stop()
        self.watcher = None

    def __timer_cb(self, watcher, revents):
        data = self.host.get_info("eth0")
        self.__raw_send("\xFF\xFF\xFF\xFF\xFF\xFF", const.RAW_BRAODCAST_REQ, len(data), data)
        self.watcher_timer.set(30, 0)
        self.watcher_timer.start()

    def broadcast_timer(self):
        data = self.host.get_info("eth0")
        self.__raw_send("\xFF\xFF\xFF\xFF\xFF\xFF", const.RAW_BRAODCAST_REQ, len(data), data)
        self.watcher_timer.start()

    def __handle_buffer(self):
        self.flag = False
        while True:
            while len(self.buffer) > const.RAW_HEADER_LEN:
                try:
                    header = struct.unpack("!6s6sHI2BHB", self.buffer[:const.RAW_HEADER_LEN])
                    #判断标志位magic是否正确
                    if header[3] == const.MAGIC:
                        break
                    else:
                        self.buffer = self.buffer[1:]
                except Exception:
                    self.buffer = self.buffer[1:]
            if len(self.buffer) < const.RAW_HEADER_LEN:
                break
            data_len = header[6]
            #剩下数据长度不够一个完整包
            if len(self.buffer) < const.RAW_HEADER_LEN + data_len:
                break
            data = self.buffer[const.RAW_HEADER_LEN:const.RAW_HEADER_LEN + data_len]
            self.__handle_raw_msg(header, data)
            #取出完整包，把剩下部分数据重新赋给buffer，相当于删除前面一个完整包
            self.buffer = self.buffer[const.RAW_HEADER_LEN + data_len:]
        if self.flag:
            self.server.resource_start()

    def __handle_raw_msg(self, header, data):
        if header[7] == const.RAW_BRAODCAST_RSP:
            log.debug("raw_socket recv:%s"%(data))
            try:
                packet = json.loads(data)
            except Exception:
                log.exception("")
                return
            try:
                vm_id = packet["vm_id"]
                vm_ip = packet["vm_ip"]
                vm_mask = packet["vm_mask"]
                vm_gateway = packet["vm_gateway"]
                center_ip = packet["dns_ip"]
            except Exception:
                log.exception("")
                return
            self.watcher_timer.stop()
            self.config.set_vm_id(vm_id)
            self.config.set_center_ip(center_ip)
            self.host.set_dns(center_ip)
            self.host.set_ip(vm_ip, vm_mask, vm_gateway)
            self.flag = True

    def __raw_send(self, mac, msg_type, data_len, data):
        #”!6s6sHI2BHB“后面需要加上“长度s”，长度提前不知道
        packet_style = "!6s6sHI2BHB%us"%(data_len)
        log.debug("send:packet_style=%s"%(packet_style))
        packet = struct.pack(packet_style, mac, self.host.get_mac("eth0"), const.PROTO, const.MAGIC, const.RAW_VERSION, const.PACKET_HEADER_LEN, data_len, msg_type, data)
        #计算格式后字符串大小
        packet_len = struct.calcsize(packet_style)
        self.__send(packet, packet_len)

    def __send(self, data, len):
        log.debug(repr(data))
        total_send = 0
        while total_send < len:
            try:
                sent = self.raw_socket.send(data[total_send:])
                #处理正常关闭
                if sent == 0:
                    log.debug("close raw_socket")
                    self.__close()
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
                    log.exception("close raw_socket")
                    self.__close()

#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import json
import struct

socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
socket.connect("/wns/data/com_host/etc/config/com_host.sock")
"""
rsp_data = {}
rsp_data["cid"] = "222222"
try:
    data_temp = json.dumps(rsp_data)
except Exception, err_msg:
    print err_msg
data_len = len(data_temp)
packet_style = "!3I%us"%(data_len)
packet = struct.pack(packet_style, 0x11237202, 1, data_len, data_temp)
packet_len = struct.calcsize(packet_style)
appinit_socket.send(packet)
"""

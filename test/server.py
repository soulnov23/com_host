#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import struct

raw_socket = socket.socket(socket.PF_PACKET,socket.SOCK_RAW,socket.htons(0x1234))

while True :
    print "recv begin"
    packet = raw_socket.recv(1024)
    print "recv end"
    print repr(packet)
    data = struct.unpack("!6s6sH12s", packet)
    print repr(data[0])
    print repr(data[1])
    print repr(data[2])
    print repr(data[3])
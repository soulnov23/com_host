#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import struct

raw_socket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x1234))
raw_socket.bind(("eth0", 0))
packet = struct.pack("!6s6sH", "\xff\xff\xff\xff\xff\xff", "\xaa\xaa\xaa\xaa\xaa\xaa", 0x1234)
while True :
    raw_socket.send(packet + "hello,world!")
    print repr(packet)

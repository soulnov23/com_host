#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import select

send_data = "hello world!"
send_len = len(send_data)
recv_len = 1024
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
addr = ("0.0.0.0", 8765)
tcp_socket.bind(addr)
tcp_socket.listen(5)
tcp_socket.setblocking(False)
epoll = select.epoll()
epoll.register(tcp_socket.fileno(), select.EPOLLIN)
fd_to_socket = {tcp_socket.fileno():tcp_socket}

while True :
    events = epoll.poll(-1)
    for fd, event in events:
        fd_socket = fd_to_socket[fd]
        if fd == tcp_socket.fileno():
            while True:
                try:
                    new_socket, new_addr = fd_socket.accept()
                except socket.error as e:
                    (errno, err_msg) = e
                    print errno
                    print err_msg
                    if errno == 11:
                        break
                print "new accpet:", new_addr
                new_socket.setblocking(False)
                new_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                epoll.register(new_socket.fileno(), select.EPOLLIN)
                fd_to_socket[new_socket.fileno()] = new_socket
        elif event&select.EPOLLIN:
            recv_datas = []
            recd = 0
            while (recd < recv_len):
                try:
                    recv_data = fd_socket.recv(recv_len - recd)
                    if recv_data == "":
                        print "close socket"
                        epoll.unregister(fd)
                        fd_socket.close()
                        del fd_to_socket[fd]
                        break
                    else:
                        recv_datas.append(recv_data)
                        recd = recd + len(recv_data)
                except socket.error as e:
                    (errno, err_msg) = e
                    print errno
                    print err_msg
                    if errno == 11:
                        break
                    elif errno == 4:
                        continue
                    else:
                        print "close socket"
                        epoll.unregister(fd)
                        fd_socket.close()
                        del fd_to_socket[fd]
                        break
                print repr(recv_datas)
                total_send = 0
                while total_send < send_len:
                    sent = fd_socket.send(send_data[total_send:])
                    if sent == 0:
                        print "close socket"
                        epoll.unregister(fd)
                        fd_socket.close()
                        del fd_to_socket[fd]
                        break
                    else:
                        print repr(send_data[total_send:])
                        total_send = total_send + sent
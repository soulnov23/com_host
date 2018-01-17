#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import os
import pyev
import traceback

def close(watcher):
    socket_temp = fd_to_socket[watcher.fd]
    socket_temp.close()
    watcher.stop()
    watcher = None

def read_cb(watcher, revents):
    print "read_cb"
    if revents & pyev.EV_READ:
        while True:
            socket_temp = fd_to_socket[watcher.fd]
            try:
                recv_data = socket_temp.recv(1024)
                # 处理正常关闭
                if recv_data == "":
                    print "close"
                    close(watcher)
                    return
                else:
                    buffer += recv_data
            #处理异常关闭(EAGAIN,EINTR)
            except socket.error as e:
                (errno, err_msg) = e
                if errno == 11:
                    break
                elif errno == 4:
                    continue
                else:
                    print "close"
                    close(watcher)
                    return

def accept_cb(watcher, revents):
    if revents & pyev.EV_READ:
        while True:
            try:
                global new_watcher
                new_socket, new_addr = resolver_socket.accept()
                fd_to_socket[new_socket.fileno()] = new_socket
                new_socket.setblocking(False)
                new_watcher = pyev.Io(new_socket, pyev.EV_READ, loop, read_cb)
                new_watcher.start()
            except Exception as e:
                (errno, err_msg) = e
                if errno == 11:
                    print "break"
                    break

if __name__ == '__main__':
    buffer = bytes()
    fd_to_socket = {}
    loop = pyev.default_loop()
    resolver_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    if os.path.exists("/wns/data/com_host/etc/config/com_host.sock"):
        os.unlink("/wns/data/com_host/etc/config/com_host.sock")
    resolver_socket.bind("/wns/data/com_host/etc/config/com_host.sock")
    resolver_socket.listen(5)
    resolver_socket.setblocking(False)
    watcher = pyev.Io(resolver_socket, pyev.EV_READ, loop, accept_cb)
    watcher.start()
    loop.start()
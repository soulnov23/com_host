#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import struct

"""
/* header for appinitd msg  */
typedef struct
{
	unsigned short	version;	/* version for the msg */
	unsigned short	msgtype;	/* message type */
	unsigned int	cmdlen; 	/* real cmd string lenth */
	char*			cmd[0]; 	/* real cmd string */
}appinitd_msg_cmd_st;
/* msg receive from appinitd struct */
typedef	struct
{
	unsigned int	datalen;		/* received msg real lenth */
	char	data[MESS_MAX_LEN];		/* received message from appinitd */
}appinitd_msg_recv_st;
"""

class appinit_client:

    APPINITD_MSG_VERSION = 0x0100
    APPINITD_MSG_CMD = 1
    APPINITD_MSG_HEARTBEAT = 2
    MESS_MAX_LEN = 2048
    APPINITD_PIPE_PATH = "/wns/var/sock/appinit.sock"

    def __init__(self):
        print "net_work __init__"
        self.appinit_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.appinit_socket.connect(self.APPINITD_PIPE_PATH)
        #self.appinit_socket.setblocking(False)
        self.appinit_data_buffer = bytes()
        self.appinit_header_size = 8
        #self.vm_status_timer = threading.Timer(2, self.__vm_status_fun)
            
    def __del__(self):
        class_name = self.__class__.__name__
        print class_name, "__del__"
    
    def start(self):
        packet = struct.pack("!2HI17s", self.APPINITD_MSG_VERSION, self.APPINITD_MSG_CMD, "appinit_cli info")
        packet_len = struct.calcsize(packet_style)
        print repr(packet)
        self.appinit_socket.send(packet)
        data = self.appinit_socket.recv(MESS_MAX_LEN)
        print repr(data)
        
if ( __name__ == "__main__"):
    print "main"
    appinit_cli = appinit_client()
    appinit_cli.start()

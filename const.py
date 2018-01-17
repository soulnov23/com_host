#!/usr/bin/python
# -*- coding: UTF-8 -*-

#raw socket宏定义
PROTO = 0xa990
MAGIC = 0xa990a990
PACKET_HEADER_LEN = 9
RAW_VERSION = 1
RAW_HEADER_LEN = 23
RAW_BRAODCAST_REQ = 1
RAW_BRAODCAST_RSP = 2
#unix socket宏定义
UNIX_SOCKET_MAGIC = 0xb9b9b9b9
UNIX_SOCKET_VERSION = 1
UNIX_SOCKET_HEADER_LEN = 20
WAC_HEATBEAT = 1
RESOLVER_REQ = 2
RESOLVER_RSP = 3
APPINIT_CLI_INFO = 4
#com_host.sh脚本路径
COM_HOST_SHELL_PATH = "/wns/shell/com_host.sh"
#sdregistry_util.sh脚本路径
SDREGISTRY_SHELL_PATH = "/wns/shell/sdregistry_util.sh"
#com_host配置
COM_HOST_JSON_PATH = "/wns/data/com_host/etc/config/com_host.json"
#上一次docker启动配置
DOCKER_INFO_CFG = "/wns/data/com_host/etc/config/docker_info.json"
#registry.crt保存路径
REGISTRY_CRT = "/wns/data/com_host/etc/config/registry.crt"
#unix socket
COM_HOST_SOCK_PATH = "/wns/data/com_host/run/com_host.sock"
#com_host.sock volume
COM_HOST_SOCK_VOLUME = "/wns/data/mt_data/com_host/run/:/var/run/com_host/"
#构造host.before的路径
PATH_HOST_BEFORE = "/tmp/host.before"
#中心端docker启动配置
CENTER_INFO_CFG = "/wns/etc/com_host/center_com.json"
VERSION_CFG = "/wns/version"
#socket.error错误码
EINTR = 4
EAGAIN = 11

#主题分段长度
TOPIC_SPLIT_SIZE = 9
#主题分段
CROSS_PLATFORM  = 1
DST_MOD         = 2
DST_DOCKER      = 3
DST_PID         = 4
SRC_MOD         = 5
SRC_DOCKER      = 6
SRC_PID         = 7
MSG_TYPE        = 8

# mqtt消息类型定义
MSG_DOCKER_UPDATE = "DOCKER_UPDATE"
MSG_DOCKER_UPGRADE = "MT_UPGRADE"
MSG_MT_MOV_SEND = "MT_MOV_SEND"
MSG_MT_MOV_RECV = "MT_MOV_RECV"

'''
租户迁移升级状态机图
prepare -> start -> data_ok -> docker_ok -> finish
            |          |            |            
            |          |            |            
            ------------------------------> fail
'''
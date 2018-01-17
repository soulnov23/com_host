#!/usr/bin/python
# -*- coding: UTF-8 -*-

import const
import time
import pyev
import signal
import json
from registry import registry
from host import host
from config import config
from wac_tunnel import wac_tunnel
from cloud_tunnel import cloud_tunnel
from mqtt_client import mqtt_client
from mongo_client import mongo_client
from docker_com import docker_com
from com_host_update import com_host_update
from status import status
from bson.objectid import ObjectId
from log import log

class server:

    def __init__(self):
        self.loop = pyev.default_loop()
        #注册退出信号SIGINT SIGTERM
        STOPSIGNALS = (signal.SIGINT, signal.SIGTERM)
        self.signal_list = [pyev.Signal(sig, self.loop, self.__signal_cb)
                             for sig in STOPSIGNALS]
        #signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        self.host = host()
        self.config = config()
        self.inner_mongo = mongo_client()
        self.outside_mongo = mongo_client()
        self.rsc_mongo = mongo_client()
        self.mqtt = mqtt_client(self.__on_message, self.loop)
        self.com_host_update = com_host_update(self)
        self.status = status(self)
        self.docker = docker_com(self)
        self.flag = True
        self.cloud_tunnel = cloud_tunnel(self)
        #资源给mqtt发送心跳包定时器
        self.watcher_timer = pyev.Timer(30, 0, self.loop, self.__timer_cb)

    def __heart_beat(self):
        rsc_id = self.config.get_vm_id()
        topic = "/rsc/cloud_srvd/0/0/com_host/%s/%u/%s"%(rsc_id, 0, "HEARTBEAT")
        data = {}
        data["rsc_id"] = rsc_id
        try:
            payload = json.dumps(data)
        except Exception:
            log.exception("")
            payload = ""
        self.mqtt.publish(topic, payload)

    def __timer_cb(self, watcher, revents):
        self.__heart_beat()
        self.watcher_timer.set(30, 0)
        self.watcher_timer.start()

    def __signal_cb(self, watcher, revents):
        self.loop.stop(pyev.EVBREAK_ALL)
        self.flag = False
        log.debug("com_host stopped")

    #按理是要设为私有接口，但是在raw_socket类中收到广播回复后需要回调，所以设为共有接口
    def resource_start(self):
        if self.inner_mongo.connect("inner.db.sdwan", 27017):
            log.debug("inner mongodb connect success")
        #从inner.db.sdwan获取最新registry.crt证书
        registry_temp = registry()
        while True:
            registry_temp.registry_crt(self.inner_mongo)
            if registry_temp.registry_init(self.config.get_center_ip()):
                break
            else:
                time.sleep(30)

        #启动com_host检查更新
        self.com_host_update.update_timer()

        if self.outside_mongo.connect("db.sdwan", 37017):
            log.debug("outside mongodb connect success")
        if self.rsc_mongo.connect("db.sdwan", 27017):
            log.debug("resource mongodb connect success")
        #启动资源状态上报定时器
        self.status.vm_status_timer()
        #检查是否是mongo_docker资源需要上报mongo状态
        self.status.mongo_status_timer()

        self.mqtt.connect("mq.sdwan", 1883)
        topic = "/cloud/com_host/%s/#"%(str(self.config.get_vm_id()))
        self.mqtt.subscribe(topic)

        self.wac_tunnel = wac_tunnel(self)
        self.docker.upgrade()
        self.docker.mov_send_task()
        self.docker.mov_recv_task()
        self.docker.resource_run()
        self.docker.resource_restart_timer()
        self.__heart_beat()
        self.watcher_timer.start()

    def __cloud_start(self):
        self.config.set_center_ip(self.host.get_ip("eth0"))
        self.host.set_dns(self.host.get_ip("eth0"))
        self.docker.cloud_run()
        self.docker.cloud_restart_timer()

    def start(self):
        if self.host.is_center():
            self.__cloud_start()
        else:
            self.cloud_tunnel.broadcast_timer()
        #启动信号事件，套接字事件在类中已经启动
        for watcher in self.signal_list:
            watcher.start()
        while self.flag:
            self.mqtt.loop(0.1)
            self.loop.start(pyev.EVRUN_NOWAIT)

    def __on_message(self, client, userdata, message):
        log.debug("Received message '%s' on topic '%s' with Qos %s retain %s"%(str(message.payload), message.topic, 
        str(message.qos), message.retain))
        ret, dst_mod, dst_docker, dst_pid, msg_type = \
            self.mqtt.get_field_from_topic(message.topic)
        if False == ret:
            return
        try:
            payload = json.loads(message.payload)
        except ValueError:
            err_info = "mqtt:%s payload error"%(msg_type)
            log.debug(err_info)
            return

        if const.MSG_DOCKER_UPDATE == msg_type:
            self.docker.resource_run()
        if const.MSG_DOCKER_UPGRADE == msg_type:
            self.docker.upgrade()
        elif const.MSG_MT_MOV_SEND == msg_type:
            self.docker.mov_send_task()
        elif const.MSG_MT_MOV_RECV == msg_type:
            self.docker.mov_recv_task()
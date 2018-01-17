#!/usr/bin/python
# -*- coding: UTF-8 -*-

import paho.mqtt.client as mqtt
from log import log
import sys
import const
import pyev
import time

class mqtt_client:

    def __init__(self, on_message, loop):
        self.client = mqtt.Client()
        self.client.on_connect = self.__on_connect
        self.client.on_disconnect = self.__on_disconnect
        self.client.on_message = on_message
        self.topic_list = []
        self.watcher_timer = pyev.Timer(30, 0, loop, self.__timer_cb)
        self.is_ok = False

    def __timer_cb(self, watcher, revents):
        try:
            self.client.reconnect()
            self.is_ok = True
        except Exception:
            log.exception("")
            self.watcher_timer.set(30, 0)
            self.watcher_timer.start()

    def connect(self, host, port):
        try:
            self.client.connect(host, port)
            self.is_ok = True
        except Exception:
            log.exception("")
            self.watcher_timer.start()

    def loop(self, timeout):
        if self.is_ok:
            self.client.loop(timeout)
        else:
            time.sleep(timeout)

    def subscribe(self, topic):
        self.topic_list.append(topic)

    def publish(self, topic, payload):
        try:
            result, mid = self.client.publish(topic, payload, 0)
        except Exception:
            log.exception("")
            return

    #调用self.client.connect时会触发一次，后续从失去连接到自动找回连接又触发
    def __on_connect(self, client, userdata, flags, rc):
        log.debug("mqtt connect success result: %s"%(str(rc)))
        for topic in self.topic_list:
            result, mid = self.client.subscribe(topic, 0)
            if result == mqtt.MQTT_ERR_SUCCESS:
                log.debug("subscribe '%s' success"%(topic))
            else:
                log.error("subscribe '%s' failed"%(topic))

    def __on_disconnect(self, client, userdata, rc):
        log.debug("on_disconnect")
        self.is_ok = False
        try:
            self.client.reconnect()
            self.is_ok = True
        except Exception:
            log.exception("")
            self.watcher_timer.start()

    def get_field_from_topic(self, topic):
        '''解析topic'''
        ret = False
        fields = topic.split('/')
        if len(fields) < const.TOPIC_SPLIT_SIZE:
            log.error('topic invalid, drop it')
            return ret, "", "", 0, ""
        ret = True
        return ret, fields[const.SRC_MOD], \
            fields[const.SRC_DOCKER], \
            int(fields[const.SRC_PID]), \
            fields[const.MSG_TYPE]
    

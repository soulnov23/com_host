#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import os

class logger:

    def __init__(self):
        class_name = self.__class__.__name__
        logger_name = "com_host"
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)

        log_path = "/home/test/com_host.log"
        path = os.path.split(log_path)[0]
        if not os.path.isdir(path):
            os.makedirs(path)
        self.fh = logging.FileHandler(log_path)
        self.fh.setLevel(logging.DEBUG)
        
        #fmt = "%(asctime)-15s [%(levelname)s] File \"%(filename)s\",line %(lineno)d: %(message)s"
        fmt = "[%(levelname)s] File \"%(filename)s\",line %(lineno)d, in %(funcName)s: %(message)s"
        #datefmt = "%a %d %b %Y %H:%M:%S"
        #self.formatter = logging.Formatter(fmt, datefmt)
        self.formatter = logging.Formatter(fmt)

        self.fh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)

    def __del__(self):
        class_name = self.__class__.__name__

    def debug(self, data):
        self.logger.debug(data)
        
    def warn(self, data):
        self.logger.warn(data)
        
    def error(self, data):
        self.logger.error(data)

log = logger()

if (__name__ == "__main__"):
    print "main"

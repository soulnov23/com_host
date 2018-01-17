#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import os

class logger:

    def __init__(self):
        logger_name = "com_host"
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)

        log_path = "/wns/data/com_host/etc/config/err.log"
        path = os.path.split(log_path)[0]
        if not os.path.isdir(path):
            os.makedirs(path)
        self.fh = logging.FileHandler(log_path)
        self.fh.setLevel(logging.DEBUG)

        fmt = "%(asctime)-15s [%(levelname)s] File \"%(filename)s\",line %(lineno)d, in %(funcName)s: %(message)s"
        datefmt = "%a %d %b %Y %H:%M:%S"
        self.formatter = logging.Formatter(fmt, datefmt)

        self.fh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)

log_temp = logger()
log = log_temp.logger

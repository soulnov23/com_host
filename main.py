#!/usr/bin/python
# -*- coding: UTF-8 -*-

from server import server
from log import log

if ( __name__ == "__main__"):
    log.debug("main")
    server = server()
    server.start()
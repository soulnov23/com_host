#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
import psutil

'''
for x in range(3):
    print psutil.cpu_times_percent(interval=1, percpu=False)
    print psutil.cpu_times_percent(interval=1, percpu=False).user
    
print psutil.virtual_memory()
print psutil.virtual_memory().percent
print psutil.disk_usage("/")
print psutil.disk_usage("/").percent
'''
for x in range(3):
    print psutil.disk_io_counters()
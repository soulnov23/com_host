#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# import json
# import traceback
#
# seg_table = []
# seg_table.append("1")
# seg_table.append("2")
# seg_table.append("3")
# try:
#     with open("./seg_table", "w") as f:
#         json.dump(seg_table, f)
# except Exception:
#     print traceback.format_exc()
# try:
#     with open("./seg_table", "r") as f:
#         temp = json.load(f)
# except Exception:
#     print traceback.format_exc()
# print type(temp)
# print temp
"""
import subprocess
cmd = "docker ps -a  --format \"{{.Names}}\" | grep -v com_host"
try:
    result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    print result
    temp = result.splitlines(False)
    print type(temp)
    print repr(temp)
except subprocess.CalledProcessError, exc:
    print exc.output
dict = {}
dict[0] = ("abc", "bcd")
dict[1] = ("cde", "def")
print repr(dict)
values = dict.values()
for a in values:
    print a
if ("abc", "bcd") in values:
    print a
dict = {}
dict["a"] = "abc"
print dict
dict["a"] = "cde"
print dict
import os
import time
import subprocess
import traceback
rsync_cmd = "rsync -a /wns/data/test1/ /wns/data/test2"
try:
    proc_child = subprocess.Popen(rsync_cmd, shell=True, stdout=subprocess.PIPE)
    print proc_child.pid
except Exception:
    print traceback.format_exc()
while True:
    try:
        (pid, ret) = os.waitpid(proc_child.pid, os.WNOHANG)
        print "pid:%d ret:%d"%(pid, ret)
        if ret:
            print "exit"
            break
    except Exception:
        print traceback.format_exc()
        break
    time.sleep(0.01)
"""
str1 = "sdwan.io:5000/sdw_db:1.0-20171221"
str2 = "sdwan.io:5000/wac_docker:1.0-2017122003"
temp1 = str1.split(":")
print repr(temp1)
temp2 = str2.split(":")
print repr(temp2)
temp = "%s:%s"%(temp1[0], temp1[1])
print repr(temp)



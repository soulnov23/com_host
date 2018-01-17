#!/usr/bin/python
# -*- coding: UTF-8 -*-

import commands
import json

command = "docker stats --no-stream --format \"{{.Name}},{{.CPUPerc}},{{.MemPerc}},{{.BlockIO}},{{.NetIO}}\""
status, output = commands.getstatusoutput(command)
output = output.splitlines(False)
for line in output:
    #print repr(line)
    data = line.split(",")
    print data[0]
    print data[1]
    print data[2]
    print data[3]
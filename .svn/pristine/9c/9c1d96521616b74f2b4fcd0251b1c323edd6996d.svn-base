#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pymongo.errors import ConnectionFailure
from pymongo import MongoClient

data = [
    {
        "name":"sdw_center", 
        "com_id":1,
        "env":"",
        "dns":"{center_ip}",
        "pipework":"192.168.0.2/24@192.168.0.254",
        "udp":[
                {"port":1234},
                {"port":2345},
                ],
        "tcp":[
                {"port":1234},
                {"port":2345},
                ],
        "volumes":[
                {"path":"/wns/data/mt_data/{cont_name}/etc/data:/wns/data/"},
                {"path":"/var/run/docker.sock:/var/run/docker.sock"},
                {"path":"/etc/hwinfo:/etc/hwinfo:ro"},
                {"path":"/wns/version:/wns/version:ro"}
                ],
        "image":"{sdw_center}",
        "host_before":"",
        "cmd":"bash"
    },
    {
        "name":"sdw_web", 
        "com_id":2,
        "env":"",
        "dns":"{host_ip}",
        "pipework":"192.168.0.3/24@192.168.0.254",
        "udp":[
                {"port":1234},
                {"port":2345},
                ],
        "tcp":[
                {"port":1234},
                {"port":2345},
                ],
        "volumes":[
                {"path":"/var/run/docker.sock:/var/run/docker.sock"},
                {"path":"/etc/hwinfo:/etc/hwinfo:ro"},
                {"path":"/wns/version:/wns/version:ro"}
                ],
        "image":"{sdw_web}",
        "host_before":"",
        "cmd":"bash"
    },
    {
        "name":"sdw_svn", 
        "com_id":3,
        "env":"",
        "dns":"{center_ip}",
        "pipework":"192.168.0.4/24@192.168.0.254",
        "udp":[
                {"port":1234},
                {"port":2345},
                ],
        "tcp":[
                {"port":1234},
                {"port":2345},
                ],
        "volumes":[
                {"path":"/var/run/docker.sock:/var/run/docker.sock"},
                {"path":"/etc/hwinfo:/etc/hwinfo:ro"},
                {"path":"/wns/version:/wns/version:ro"}
                ],
        "image":"{sdw_svn}",
        "host_before":"",
        "cmd":"bash"
    },
    {
        "name":"sdw_db", 
        "com_id":4,
        "env":"",
        "dns":"{host_ip}",
        "pipework":"192.168.0.5/24@192.168.0.254",
        "udp":[
                {"port":1234},
                {"port":2345},
                ],
        "tcp":[
                {"port":1234},
                {"port":2345},
                ],
        "volumes":[
                {"path":"/wns/data/mt_data/{cont_name}/etc/data:/wns/data/"},
                {"path":"/var/run/docker.sock:/var/run/docker.sock"},
                {"path":"/etc/hwinfo:/etc/hwinfo:ro"},
                {"path":"/wns/version:/wns/version:ro"}
                ],
        "image":"{sdw_db}",
        "host_before":"",
        "cmd":"bash"
    },
    {
        "name":"sdw_test", 
        "com_id":5,
        "env":"",
        "dns":"{host_ip}",
        "pipework":"192.168.0.5/24@192.168.0.254",
        "udp":[
                {"port":1234},
                {"port":2345},
                ],
        "tcp":[
                {"port":1234},
                {"port":2345},
                ],
        "volumes":[
                {"path":"/wns/data/mt_data/{cont_name}/etc/data:/wns/data/"},
                {"path":"/var/run/docker.sock:/var/run/docker.sock"},
                {"path":"/etc/hwinfo:/etc/hwinfo:ro"},
                {"path":"/wns/version:/wns/version:ro"}
                ],
        "image":"{sdw_db}",
        "host_before":"",
        "cmd":"bash"
    }
]

if ( __name__ == "__main__"):
    print "main"
    mongo_client = MongoClient(host="10.51.23.55", port=27017, serverSelectionTimeoutMS=1)
    try:
        mongo_client.admin.command("ping")
    except ConnectionFailure:
        print "connect error"
    db = mongo_client["zcp"]
    col = db["test"]
    result = col.insert_many(data)
    print result.inserted_ids
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import subprocess
import const
from log import log

class registry:

    def registry_init(self, ip):
        command = "bash %s install %s %s"%(const.SDREGISTRY_SHELL_PATH, ip, const.REGISTRY_CRT)
        log.debug(repr(command))
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            log.debug(result)
        except subprocess.CalledProcessError, exc:
            log.error(exc.output)
            return False
        return True

    def registry_crt(self, mongo):
        try:
            result = mongo.find_one("inner_db", "crt_tbl", {"crt_name":"registry_crt"})
        except Exception:
            log.exception("")
        if result:
            data = result.get("crt_data", "")
            if data == "":
                log.error("crt_tbl of inner_db not exist registry.crt data")
            try:
                with open(const.REGISTRY_CRT, "w") as f:
                    f.write(data)
            except Exception:
                log.exception("")
        else:
            log.error("crt_tbl of inner_db not exist registry.crt data")
#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pymongo import MongoClient
from log import log
import sys
import json

class mongo_client:

    def __init__(self):
        self.client = None

    def __del__(self):
        if self.client is not None:
            self.client.close()

    def connect(self, host, port):
        count = 0
        while True:
            self.client = MongoClient(host, port, serverSelectionTimeoutMS=3)
            try:
                self.client.admin.command("ping")
            except Exception:
                log.exception("")
                count = count + 1
            else:
                break
            if count == 3:
                return False
        return True

    def find_one(self, db_name, col_name, query):
        db = self.client[db_name]
        col = db[col_name]
        result = {}
        result = col.find_one(query)
        return result

    def find(self, db_name, col_name, query={}):
        db = self.client[db_name]
        col = db[col_name]
        result = []
        result = col.find(query)
        return result

    def insert_one(self, db_name, col_name, data):
        db = self.client[db_name]
        col = db[col_name]
        result = col.insert_one(data)

    def delete_one(self, db_name, col_name, filter):
        db = self.client[db_name]
        col = db[col_name]
        result = col.delete_one(filter)

    def delete_many(self, db_name, col_name, filter):
        db = self.client[db_name]
        col = db[col_name]
        result = col.delete_many(filter)

    def update(self, db_name, col_name, filter, set):
        db = self.client[db_name]
        col = db[col_name]
        result = col.update(filter, set)
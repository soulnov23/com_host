#!/usr/bin/python
# -*- coding: UTF-8 -*-

class test1:
    def __init__(self, test):
        self.test2 = test
        
    def fun1(self):
        self.test2.fun3()
        print self.test2.data
        
class test2:
    def __init__(self):
        self.data = "world"
        
    def fun2(self):
        test = test1(self)
        test.fun1()
        
    def fun3(self):
        print "hello"

if (__name__ == "__main__"):
    test = test2()
    test.fun2()

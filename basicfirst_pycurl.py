#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4:et
import sys
import pycurl, json
from io import BytesIO

PY3 = sys.version_info[0] > 2


class Test:
    def __init__(self):
        self.contents = ''
        if PY3:
            self.contents = self.contents.encode('ascii')

    def body_callback(self, buf):
        self.contents = self.contents + buf


sys.stderr.write("Testing %s\n" % pycurl.version)
baseurl = "https://en.wikipedia.org/w/api.php?"
fmt = "format=json&"
act = "action=query&"
lst = "list=categorymembers&"
nms = "cmnamespace=14&"
lim = "cmlimit=100&"
url_string = baseurl + fmt + act + lst + nms + lim + "cmtitle=Category:Machine%20learning"
data = BytesIO()
t = Test()
c = pycurl.Curl()
c.setopt(c.URL, url_string)
c.setopt(c.WRITEFUNCTION, data.write)
c.perform()
c.close()
dtext = data.getvalue().decode('UTF-8')
jdata = json.loads(dtext)
print(dtext)
data.close()
print(jdata['continue'])

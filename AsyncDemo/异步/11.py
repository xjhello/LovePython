#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/10/2 1:23
@Author  : Xu_Jian
"""
import json

import requests

url = "http://{0}:{1}/api/rcs/warehouse/{2}/agv/status/by_condition".format('10.57.118.152', '9001',1)
parameters = {"agvIds": "CARRIER_10572414"}
headers = {'Content-Type': 'application/json','Accept': 'application/json'}
aa = requests.post(url=url, headers=headers, data=json.dumps(parameters)).text
print(aa)
# response_data = json.loads()

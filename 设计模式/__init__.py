#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/15 4:59 下午
# @Author  : Xujian
import json

a = {'layers': [{'shapes': [{'radius': 450,
                             'points': [{'y': 2600, 'x': 8470}, {'y': 2600, 'x': 6030}, {'y': 3400, 'x': 6030},
                                        {'y': 3400, 'x': 8470}], 'type': 1, 'center': {'y': 3000, 'x': 8000}},
                            {'radius': 0,
                             'points': [{'y': 2600, 'x': 8470}, {'y': 2600, 'x': 6030}, {'y': 3400, 'x': 6030},
                                        {'y': 3400, 'x': 8470}], 'type': 0, 'center': {'y': 3000, 'x': 8000}},
                            {'radius': 450,
                             'points': [{'y': 2600, 'x': 8470}, {'y': 2600, 'x': 6030}, {'y': 3400, 'x': 6030},
                                        {'y': 3400, 'x': 8470}], 'type': 1, 'center': {'y': 3000, 'x': 6500}}],
                 'layer': 1, 'top': 1000, 'bottom': 0}], 'paths': [
    {'control1': {'y': 0, 'x': 0}, 'start': {'y': 8000, 'x': 8000}, 'type': 0, 'target': {'y': 8100, 'x': 8100},
     'control2': {'y': 0, 'x': 0}},
    {'control1': {'y': 0, 'x': 0}, 'start': {'y': 3000, 'x': 8000}, 'type': 0, 'target': {'y': 3000, 'x': 6500},
     'control2': {'y': 0, 'x': 0}},
    {'control1': {'y': 0, 'x': 0}, 'start': {'y': 3000, 'x': 6500}, 'type': 0, 'target': {'y': 3100, 'x': 6600},
     'control2': {'y': 0, 'x': 0}}], 'msgId': '85db1832-5d9f-11ec-bd01-0242ac110002', 'ownerType': 0, 'jobId': 'test',
     'robotCode': 'CARRIER_001', 'position': {'pointCode': '', 'x': 8000, 'lineCode': '', 'y': 3000}}
aaa = {'source': None, 'result': True, 'errorMessage': None, 'data': {'layers': [{u'shapes': [{u'type': u'CIRCLE', u'points': [], u'radius': 450, u'center': {u'y': 1000, u'x': 9500}}, {u'type': u'POLYGON', u'points': [{u'y': 1500, u'x': 9900}, {u'y': 530, u'x': 9900}, {u'y': 530, u'x': 9100}, {u'y': 1500, u'x': 9100}], u'radius': 0}], u'layer': 1, u'top': 1000, u'bottom': 0}], 'truncated': True}, 'id': u'e0966ac7-ff9f-4a0d-89b2-cc00f3d85eee', 'messageType': 'ResponseLockedArea'}
print(json.dumps(aaa))
bbb= aaa["data"]["layers"]
print(bbb[0]['shapes'])
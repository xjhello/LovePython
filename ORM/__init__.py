#!/usr/bin/env python
# -*- coding: utf-8 -*-


a = {'netStartTm': 1650297663000, 'respTimeoutMillis': 86400000,
     'mapping': {'path': '/qsh/request/traffic/spaceLock', 'type': 'REQUEST', 'mode': 'SYNC'}, 'messageType': 'DATA',
     'objects': [{'className': 'com.kc.phoenix.rts.robot.model.remote.LockSpaceRequestBO', 'value': {u'layers': [{
                                                                                                                     u'shapes': [
                                                                                                                         {
                                                                                                                             u'radius': 0,
                                                                                                                             u'points': [
                                                                                                                                 {
                                                                                                                                     u'y': -6574,
                                                                                                                                     u'x': 39803},
                                                                                                                                 {
                                                                                                                                     u'y': -7508,
                                                                                                                                     u'x': 39803},
                                                                                                                                 {
                                                                                                                                     u'y': -7508,
                                                                                                                                     u'x': 38519},
                                                                                                                                 {
                                                                                                                                     u'y': -6574,
                                                                                                                                     u'x': 38519}],
                                                                                                                             u'type': 1,
                                                                                                                             u'center': {
                                                                                                                                 u'y': -7041,
                                                                                                                                 u'x': 39161}},
                                                                                                                         {
                                                                                                                             u'radius': 0,
                                                                                                                             u'points': [
                                                                                                                                 {
                                                                                                                                     u'y': -6574,
                                                                                                                                     u'x': 38519},
                                                                                                                                 {
                                                                                                                                     u'y': -6574,
                                                                                                                                     u'x': 41003},
                                                                                                                                 {
                                                                                                                                     u'y': -7508,
                                                                                                                                     u'x': 41003},
                                                                                                                                 {
                                                                                                                                     u'y': -7508,
                                                                                                                                     u'x': 38519}],
                                                                                                                             u'type': 1,
                                                                                                                             u'center': {
                                                                                                                                 u'y': -7041,
                                                                                                                                 u'x': 39161}}],
                                                                                                                     u'layer': 1,
                                                                                                                     u'top': 250,
                                                                                                                     u'bottom': 0}],
                                                                                                     u'paths': [{
                                                                                                                    u'start': {
                                                                                                                        u'y': -7041,
                                                                                                                        u'x': 39161},
                                                                                                                    u'type': 1,
                                                                                                                    u'control1': {
                                                                                                                        u'y': 0,
                                                                                                                        u'x': 0},
                                                                                                                    u'target': {
                                                                                                                        u'y': -7041,
                                                                                                                        u'x': 39161},
                                                                                                                    u'control2': {
                                                                                                                        u'y': 0,
                                                                                                                        u'x': 0}},
                                                                                                                {
                                                                                                                    u'start': {
                                                                                                                        u'y': -7041,
                                                                                                                        u'x': 39161},
                                                                                                                    u'type': 1,
                                                                                                                    u'control1': {
                                                                                                                        u'y': 0,
                                                                                                                        u'x': 0},
                                                                                                                    u'target': {
                                                                                                                        u'y': -7041,
                                                                                                                        u'x': 40361},
                                                                                                                    u'control2': {
                                                                                                                        u'y': 0,
                                                                                                                        u'x': 0}}],
                                                                                                     u'msgId': u'b8f12da4-bf30-11ec-9b0d-0242ac110007',
                                                                                                     u'ownerType': 1,
                                                                                                     u'jobId': u'',
                                                                                                     u'robotCode': u'CARRIER_006',
                                                                                                     u'position': {
                                                                                                         u'pointCode': u'',
                                                                                                         u'x': 39161,
                                                                                                         u'lineCode': u'',
                                                                                                         u'y': -7041},
                                                                                                     u'pathVersion': u'T2022-04-19+00:00:52.285',
                                                                                                     u'ownerId': u'CARRIER_006'}}],
     'id': 'bf45d2d6-bf30-11ec-a858-0242ac110007bf45d664'}


print(a['objects'][0]['value']['pathVersion'])
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import pprint
import requests


class FindMyI(object):
    partition = None

    def __init__(self, username, password):
        self.devices = []
        self.username = username
        self.password = password
        self.headers = {
            'Content-type': 'application/json; charset=utf-8',
            'X-Apple-Find-Api-Ver': '2.0',
            'X-Apple-Authscheme': 'UserIdGuest',
            'X-Apple-Realm-Support': '1.0',
            'User-agent': 'Find iPhone/1.2 MeKit (iPad: iPhone OS/4.2.1)',
            'X-Client-Name': 'iPad',
            'X-Client-UUID': '0cf3dc501ff812adb0b202baed5f37274b210853',
            'Accept-Language': 'en-us',
            'Connection': 'keep-alive',
            'Authorization': 'Basic %s' % base64.encodestring('%s:%s' % (self.username, self.password,))[:-1],
        }

    def get_partition(self):
        payload = {
            "clientContext":{
                "appName":"FindMyiPhone",
                "appVersion":"1.4",
                "buildVersion":"145",
                "deviceUDID":"0000000000000000000000000000000000000000",
                "inactiveTime":2147483647,
                "osVersion":"4.2.1",
                "personID":0,
                "productType":"iPad1,1"
            }
        }
        
        url = 'https://fmipmobile.icloud.com/fmipservice/device/%s/initClient' % self.username
        r = requests.post(url, data=json.dumps(payload), headers=self.headers)
        if r.status_code != 401:
            self.partition = r.headers.get('X-Apple-MMe-Host')
            return True
        return False
        
    def update_devices(self):
        payload = {
            "clientContext":{
                "appName":"FindMyiPhone",
                "appVersion":"1.4",
                "buildVersion":"145",
                "deviceUDID":"0000000000000000000000000000000000000000",
                "inactiveTime":2147483647,
                "osVersion":"4.2.1",
                "personID":0,
                "productType":"iPad1,1"
            }
        }
        url = 'https://' + self.partition + '/fmipservice/device/%s/refreshClient' % self.username
        r = requests.post(url, data=json.dumps(payload), headers=self.headers)
        self.devices = []
        json_data = r.json()
        for device in json_data['content']:
            temp_device = {}
            temp_device['name'] = device['name']
            temp_device['aid'] = device['id']
            temp_device['device_display_name'] = device['deviceDisplayName']
            if device['location'] is not None:
                temp_device['located'] = device['location']['locationFinished']
                temp_device['accuracy'] = device['location']['horizontalAccuracy']
                temp_device['latitude'] = device['location']['latitude']
                temp_device['longitude'] = device['location']['longitude']
                temp_device['timestamp'] = device['location']['timeStamp']
            self.devices.append(temp_device)
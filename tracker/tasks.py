#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from tracker import celery
from database import db
from celery.signals import task_postrun
from models import User, iCloudUser, Device, Location
from tracker.findmyi import FindMyI
from pytz import timezone, utc
eastern = timezone('US/Eastern')


@celery.task
def update_account(id, username, password):
    manager = FindMyI(username, password)
    if manager.get_partition():
        manager.update_devices()
        for device in manager.devices:
            device_obj = Device.query.filter_by(aid=device['aid']).first()
            if device_obj is None:
                device_obj = Device()
                device_obj.user_id = id
                device_obj.aid = device['aid']
                device_obj.name = device['name']
                device_obj.device_name = device['device_display_name']
                db.session.add(device_obj)
                db.session.commit()
            if 'located' in device:
                print device
                location = Location(device_obj.id, device['longitude'], device['latitude'],  device['accuracy'], datetime.datetime.fromtimestamp(device['timestamp']/1000.0))
                db.session.add(location)
        db.session.commit()

@celery.task
def update_accounts(id):
    user = User.query.get(id)
    for account in user.accounts:
        update_account.delay(id, account.username, account.password)

@celery.task
def update_all():
    users = User.query.all()
    for user in users:
        update_accounts.delay(user.id)

@task_postrun.connect
def close_session(*args, **kwargs):
    if kwargs['sender']=="tasks.update_account":
        db.session.remove()
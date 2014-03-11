#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tracker.database import db
from pytz import timezone, utc
eastern = timezone('US/Eastern')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    last_login = db.Column(db.DateTime)
    accounts = db.relationship('iCloudUser', backref='user',
                               lazy='dynamic')


class iCloudUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    aid = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    locations = db.relationship('Location', backref='device',
                               lazy='dynamic')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'device_name': self.device_name,
            'location_count': self.locations.count()
        }


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    lon = db.Column(db.Float(precision=64))
    lat = db.Column(db.Float(precision=64))
    accuracy = db.Column(db.Integer)
    label = db.Column(db.Text)
    time = db.Column(db.DateTime)
    @property
    def serialize(self):
        return {
            'lon': self.lon,
            'lat': self.lat,
            'accuracy': self.accuracy,
            'time': eastern.localize(self.time).strftime("%Y/%m/%d %I:%M:%S%p %Z")
        }
    def __init__(self, device_id, lon, lat, accuracy, time):
        self.device_id, self.lon, self.lat, self.accuracy, self.time = device_id, lon, lat, accuracy, time
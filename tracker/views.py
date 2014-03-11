#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, request, jsonify, session
from tracker import app
from tracker.findmyi import FindMyI
from tasks import update_accounts, update_account
from tracker.database import db
from tracker.models import Device, User, iCloudUser, Location


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/account/check_login/')
def check_login():
    if 'user_id' in session:
        connected = False
        user = User.query.get(session['user_id'])
        if user.accounts.count():
            connected = True
        return jsonify(success=1,
                       session={'connected': connected, 'email': user.email})
    return jsonify(success=0)

@app.route('/account/login/', methods=['POST'])
def login():
    username, password = request.form['username'], request.form['password']
    user = User.query.filter_by(email=username).first()
    if user is None or user.password!=password:
        return jsonify(success=0,
                       error='xxx')
    else:
        session['user_id'] = user.id
        connected = False
        if user.accounts.count():
            connected = True
        return jsonify(success=1,
                       session={'connected': connected, 'email': user.email})

@app.route('/account/logout/', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify(success=1)


@app.route('/account/connect_icloud/', methods=['POST'])
def connect_icloud():
    username, password = request.form['username'], request.form['password']
    findmyi = FindMyI(username, password)
    if findmyi.get_partition():
        icloud_user = iCloudUser.query.filter_by(username=username).first()
        if icloud_user is None:
            icloud_user = iCloudUser(session['user_id'], username, password)
        elif icloud_user.user_id==session['user_id']:    
            icloud_user.password = password
        else:
            return jsonify(success=0,
                           error='This iCloud Account Aleady Accociated With Another Account',
                           )
        db.session.add(icloud_user)
        db.session.commit()
        update_account(icloud_user.id, username, password)
        return jsonify(success=1,
                       session={
                       }
        )
    
    return jsonify(success=0,
                   error='Incorrect Username and Password',
    )

@app.route('/account/devices/')
def load_device():
    devices = Device.query.filter_by(user_id=session['user_id']).all()
    if devices:
        device_list = [device.serialize for device in devices]
        return jsonify(success=1,
                       session={
                           'devices': device_list,
                        }
        )
    else:
        return jsonify(success=0,
                       error='No Device',
                       )

@app.route('/account/devices/history', methods=['POST'])
def device_location_history():
    if session['user_id']:
        device_id = request.form['device_id']
        device = Device.query.get(device_id)
        if device.user_id == session['user_id']:
            locations = Location.query.filter_by(device_id=device_id).order_by(Location.time.desc()).limit(500).all()
            location_list = [location.serialize for location in locations]
            location_list.reverse()
            return jsonify(success=1,
                           locations=location_list)

    return jsonify(success=0)
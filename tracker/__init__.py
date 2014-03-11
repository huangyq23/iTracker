#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from celery import Celery
app = Flask(__name__)
app.config.from_object('tracker.settings')
celery = Celery()
celery.config_from_object(app.config)

import views
import tasks
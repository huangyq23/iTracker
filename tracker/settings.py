#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import timedelta

DEBUG = True
SQLALCHEMY_DATABASE_URI = "mysql://tracker:v9042ivds9dqj02c1@localhost/tracker?charset=utf8"

SECRET_KEY = 'iJ\xbd\xf0\xa8\xbb\x1d\xc5}u\xfb\xe1\x95\xa2\x0b\xb5\xb8\xeeQ\x11\x87\xc5\xff\xb0'


BROKER_URL = 'sqla+mysql://tracker:v9042ivds9dqj02c1@localhost/tracker'
CELERY_TIMEZONE = 'America/New_York'
CELERY_ENABLE_UTC = True
CELERYBEAT_SCHEDULE = {
    'fetch-every-mintue': {
        'task': 'tracker.tasks.update_all',
        'schedule': timedelta(seconds=180),
    },
    }

CELERY_TIMEZONE = 'UTC'
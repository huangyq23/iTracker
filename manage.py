#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.script import Server, Manager
from tracker import app,celery

manager = Manager(app=app)
manager.add_command("runserver", Server())

@manager.command
def run_celery():
    celery.start()

if __name__ == "__main__":
    manager.run()
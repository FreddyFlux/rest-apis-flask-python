#!/bin/sh

flask db upgrade

exec gunicorn -b 0.0.0.0:80 "app:create_app()"
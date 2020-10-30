#!/bin/sh
source gossip_app/bin/activate
flask db upgrade
flask translate compile 
exec gunicorn -b :5000 --access-logfile - --error-logfile - gossip_app:app
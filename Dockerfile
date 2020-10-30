FROM python:3.8-alpine

RUN adduser -D gossip_app

WORKDIR /home/software_development/python/current_projects/1_work_gossip_chat_app

COPY requirements.txt requirements.txt
RUN python -m venv gossip_app
RUN gossip_app/bin/python3 -m pip  install --upgrade pip

RUN \
# install psycopg2 dependancies
 apk update && \
 apk add postgresql-dev gcc python3-dev musl-dev && \
 # then install your requirements
 gossip_app/bin/pip3 install -r requirements.txt && \
 gossip_app/bin/pip3 install gunicorn pymysql

COPY app app
COPY migrations migrations
COPY tinker.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP tinker.py

RUN chown -R gossip_app:gossip_app ./
USER gossip_app

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]
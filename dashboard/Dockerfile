FROM python:3.9-slim-buster

RUN apt-get update
RUN apt-get install nano

RUN mkdir wd
WORKDIR wd
COPY app/dashboard_requirements.txt .
RUN pip3 install -r dashboard_requirements.txt

COPY app/ ./

CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:80", "app:server"]
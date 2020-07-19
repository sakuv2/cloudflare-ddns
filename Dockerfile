FROM python:3.8-alpine


WORKDIR /root

COPY ./requirements.txt ./
RUN pip install -r requirements.txt && rm requirements.txt

COPY ./ddns.py ./

RUN echo "* * * * * python ddns.py" > /var/spool/cron/crontabs/root

ENV TZ=Asia/Tokyo

ENTRYPOINT ["busybox", "crond", "-f"]

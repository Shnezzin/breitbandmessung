FROM python:slim-bullseye

RUN  apt-get update \
     && apt-get install --no-install-recommends -y firefox-esr tini cron curl build-essential libssl-dev libffi-dev python3-dev cargo \
     && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
     selenium \
     apprise \
     psutil \
     influxdb
     
WORKDIR /usr/src/app

COPY speedtest.py config.shlib geckodriver.sh config.cfg.defaults ./

COPY entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x ./geckodriver.sh && ./geckodriver.sh

RUN chmod +x speedtest.py

RUN mkdir /export

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["tini", "--", "docker-entrypoint.sh"]

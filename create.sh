#!/bin/bash

docker build -f Dockerfile -t breitbandmessung .
chmod +x $PWD/*.sh
docker stop breitbandmessung >> /dev/null
docker rm breitbandmessung >> /dev/null
mkdir $PWD/config
mkdir $PWD/Database
mkdir $PWD/export
chmod 777 $PWD/export
docker create  -p 5800:5800 -v $PWD/config/:/opt/config:rw -v $PWD/export/:/export:rw -v $PWD/Database:/config/xdg/config/Breitbandmessung:rw --name "breitbandmessung" breitbandmessung:latest
docker start breitbandmessung
exit 0
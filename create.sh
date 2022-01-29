#!/bin/bash

docker build -f Dockerfile -t breitbandmessung .
chmod +x $PWD/*.sh
docker stop breitbandmessung >> /dev/null
docker rm breitbandmessung >> /dev/null
mkdir $PWD/config
cp config.cfg.defaults config/config.cfg
mkdir $PWD/messprotokolle
docker create -v $PWD/config/:/usr/src/app/config:rw -v $PWD/messprotokolle:/export/ --name "breitbandmessung" breitbandmessung:latest 
echo .
echo "Start the Container with 'docker run breitbandmessung'"
exit 0

#!/bin/bash

docker build -f Dockerfile -t breitbandmessung .
chmod +x $PWD/*.sh
docker stop breitbandmessung >> /dev/null
docker rm breitbandmessung >> /dev/null
mkdir $PWD/config
mkdir $PWD/messprotokolle
chmod 777 $PWD/messprotokolle
docker create -p5800:5800--name "breitbandmessung" breitbandmessung:latest 
docker start breitbandmessung
exit 0

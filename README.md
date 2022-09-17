# Breitbandmessung.de automated

A script to enable customers of lazy ISPs to perform measurement campaigns of the connection speed as described [here](https://www.bundesnetzagentur.de/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Breitband/Breitbandmessung/start.html) in an automated way.

## Usage

Create a configuration folder with the command `mkdir config` and inside the configuration folder a file `config.cfg`.

Example config.cfg:
```
[Docker Config]
timezone=Europe/Berlin
crontab=* */2 * * *
run_once=true
run_on_startup=true

[Measurement]
min-upload=600
min-download=30

[Telegram]
token=4927531485:lchtmxgr6sm7ia4g0fvbtoslruvgtway6uf
ID=42681397

[MAIL]
username=firstname.lastname
password=supersecret
maildomain=gmail.com
mailto=mail.recipient@domain.com

[Twitter]
consumerkey=T1JJ3T3L2
consumersecret=A1BRTD4JD
accesstoken=TIiajkdnlazkcOXrIdevi7F
accesssecret=FDVJaj4jcl8chG3

[influxdb]
host=influxdb
port=8086
dbname=breitbandmessung

[influxdbv2]
host=influxdb
port=8086
dbname=breitbandmessung
orgname=MyOrganizationName
token=SOYW1RRCbL6j0m5I6_UE6SMG3LHOirIhov2Y7NkPUcVHbaWIJZfdJT0h7geEaY5z42bz9SyuSjQ7GtTIsD43ev==

```

Create a folder for the measurement results with `mkdir messprotokolle`.

For the cronjob you can use [this website](https://crontab-generator.org/).
By default, the measurement is performed every 2nd full hour.

Timezone name from [this list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List).
The default timezone is UTC.

The broadband measurement can run once or automated via cron.
For a one-time measurement set the value in the config to true.



Just run:

```
git clone https://github.com/shneezin/breitbandmessung.git && cd breitbandmessung
sudo ./create.sh
```

or 

```
docker run -d -v $PWD/config/:/usr/src/app/config:rw -v $PWD/messprotokolle:/export/ --name "breitbandmessung" shneezin/breitbandmessung
```

To merge the csv files into one, run merge.sh or:
```
wget -O - https://raw.githubusercontent.com/shneezin/breitbandmessung/master/merge.sh | bash
```

Thanks to shiaky for the idea on this project. 
You can find his repo [here](https://github.com/shiaky/breitbandmessung)

## License

Feel free to use and improve the script as you like. I take no responsibility for the script.

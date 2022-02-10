from croniter import croniter
from speedtest import *
import speedtest
from datetime import datetime, timedelta
import time

readconfig()

if speedtest.MEASURMENT_MODE == 'setup':
    while True:
        sleep(20)

print('Sleep 30 sec', flush=True)
time.sleep(30)
print('Lets go', flush=True)

if speedtest.run_on_startup == 'true':
    print('Run on startup', flush=True)
    speedtest.speedtest()
    if speedtest.run_once == 'true':
        print('Only run once', flush=True)
        exit()

if speedtest.run_once == 'true':
    print('Only run once', flush=True)
    speedtest.speedtest()
    exit()

# Round time down to the top of the previous minute
def roundDownTime(dt=None, dateDelta=timedelta(minutes=1)):
    roundTo = dateDelta.total_seconds()
    if dt == None : dt = datetime.now()
    seconds = (dt - dt.min).seconds
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + timedelta(0,rounding-seconds,-dt.microsecond)

# Get next run time from now, based on schedule specified by cron string
def getNextCronRunTime(cronschedule):
    return croniter(cronschedule, datetime.now()).get_next(datetime)

# Sleep till the top of the next minute
def sleepTillTopOfNextMinute():
    t = datetime.utcnow()
    sleeptime = 60 - (t.second + t.microsecond/1000000.0)
    time.sleep(sleeptime)

cronschedule = speedtest.cronschedule
nextRunTime = getNextCronRunTime(cronschedule)
while True:
     roundedDownTime = roundDownTime()
     if (roundedDownTime == nextRunTime):

         speedtest.speedtest()

         nextRunTime = getNextCronRunTime(cronschedule)
     elif (roundedDownTime > nextRunTime):
         # We missed an execution. Error. Re initialize.
         nextRunTime = getNextCronRunTime(cronschedule)
     sleepTillTopOfNextMinute()

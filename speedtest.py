import time
import tkinter as tk
from pyautogui import *
import pyautogui
import tkinter as tk
import time
import configparser
import apprise
import os, time

def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

def readconfig():
    config = configparser.ConfigParser(allow_no_value=True)
    print(config.sections(), flush=True)
    try:
            config.read('/opt/config/config.cfg')

            if config.has_section('Docker Config'):
                    print('Section Docker Config found', flush=True)
                    global cronschedule, run_on_startup, run_once, timezone_config
                    cronschedule = config['Docker Config']['crontab']
                    run_once = config['Docker Config']['run_once']
                    run_on_startup = config['Docker Config']['run_on_startup']
                    timezone_config = config['Docker Config']['timezone']
            else:
                print('Section Docker not found', flush=True)

            if config.has_section('Measurement'):
                    print('Section Measurment found', flush=True)
                    global MEASURMENT_MODE, MIN_DOWNLOAD, MIN_UPLOAD, happy
                    happy = config['Measurement']['happy']
                    MEASURMENT_MODE = config['Measurement']['modus']
                    MIN_UPLOAD = config['Measurement']['min-upload']
                    MIN_DOWNLOAD = config['Measurement']['min-download']
            else:
                print('Section Measurment not found', flush=True)
                    
            if config.has_section('Telegram'):
                    print('Section Telegram found', flush=True)
                    global TELEGRAM_ID, TELEGRAM_TOKEN
                    TELEGRAM_TOKEN = config['Telegram']['token']
                    TELEGRAM_ID = config['Telegram']['ID']
            else:
                print('Section Telegram not found', flush=True)

            if config.has_section('MAIL'):
                    print('Section Mail found', flush=True)
                    global MAILUSER, MAILDOMAIN, MAILPASSWORD, MAILTO
                    MAILUSER = config['MAIL']['username']
                    MAILDOMAIN = config['MAIL']['maildomain']
                    MAILPASSWORD = config['MAIL']['password']
                    MAILTO = config['MAIL']['mailto']
            else:
                print('Section Mail not found', flush=True)

            if config.has_section('Twitter'):
                    print('Section Twitter found', flush=True)
                    global TWITTERAKEY, TWITTERCKEY, TWITTERASECRET, TWITTERCSECRET
                    TWITTERCKEY = config['Twitter']['consumerkey']
                    TWITTERCSECRET = config['Twitter']['consumersecret']
                    TWITTERAKEY = config['Twitter']['accesstoken']
                    TWITTERASECRET = config['Twitter']['accesssecret']
            else:
                print('Section Twiter not found', flush=True)

            print('Actual mode ist: ' + MEASURMENT_MODE, flush=True)

    except:
        return print('No configuration available', flush=True)

def click(x,y):
    x += 60
    converted_x = str(x)
    converted_y = str(y)
    print('Click button at location ' + converted_x + converted_y, flush=True)
    pyautogui.leftClick(x,y)

def sendnotification():
        try: MIN_UPLOAD and MIN_DOWNLOAD
        except:
            print('Min Up or Download not set', flush=True)
            internet_to_slow = False
        else:
            if result_up >= MIN_UPLOAD or result_down >= MIN_DOWNLOAD:
                internet_to_slow = False
                print('Internet ok', flush=True)
            else:
                internet_to_slow = True

        if internet_to_slow:
            print("Internet to slow", flush=True)
            my_message = "Current Download is: " + result_down + " " +  "MBit/s and current upload is: " + result_up + "MBit/s"
            apobj = apprise.Apprise()
            config = apprise.AppriseConfig()
            apobj.add('tgram://' + TELEGRAM_TOKEN + '/' + TELEGRAM_ID)
            apobj.add('mailto://' + MAILUSER + ':' + MAILPASSWORD + '@' + MAILDOMAIN + '?to=' + MAILTO + '?from=' + MAILUSER + '&name=Breitbandmessung Docker')
            apobj.add('twitter://' + TWITTERCKEY + '/' + TWITTERCSECRET + '/' + TWITTERAKEY + '/'+ TWITTERASECRET + '?mode=tweet')

            apobj.notify(
            body=my_message,
            title='Breitbandmessung.de Ergebnis',
            attach=screenshot,
            )

class onetime:

    def downaup():
        global result_down, result_up, screenshot
        root = tk.Tk()
        pyautogui.doubleClick(408,168)
        pyautogui.hotkey('ctrl', 'c')
        result_down = root.clipboard_get()
        print('Download: ' + result_down + ' MBit/s', flush=True)
        pyautogui.doubleClick(408,337)
        pyautogui.hotkey('ctrl', 'c')
        result_up = root.clipboard_get()
        print('Upload: ' + result_up + ' MBit/s', flush=True)
        click(408,337)
        screenshot = pyautogui.screenshot()
        click(337,340)

    def measurement():
        click(100,259)
        if happy == '1':
            click(260,490)
        elif happy == '2':
            click(415,490)
        elif happy == '3':
            click(530,490)
        elif happy == '4':
            click(670,490)
        elif happy == '5':
            click(815,490)
        elif happy == '6':
            click(940,490)
        else: 
            print('No Set', flush=True)
        time.sleep(1)
        click(1000,670)      

class kampagne:

    def measurement():
        click(115,481)
        time.sleep(1)
        click(418,520)
        click(642,407)
        click(642,488)
        click(642,555)
        click(1120,407)
        click(1120,488)
        click(1120,555)
        time.sleep(5)
        click(1037,683)

def speedtest():
    try:
        if MEASURMENT_MODE == 'einzelmessung':
            onetime.measurement() 
            time.sleep(90)
            onetime.downaup()
            sendnotification()
        elif MEASURMENT_MODE == 'kampagne':
            kampagne.measurement()
            sleep(60)
        elif MEASURMENT_MODE == 'position':
            while True:
                mouseposition = pyautogui.position()
                print(mouseposition, flush=True)
                sleep(1)
    except:
        print('No measurement type found. Possible types are: setup, einzelmessung, kampagne', flush=True)

def timezone():
    print('Setting timezone to:' + timezone_config, flush=True)
    os.environ['TZ'] = timezone_config
    time.tzset()

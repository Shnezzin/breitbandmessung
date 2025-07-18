#!/usr/local/bin/python3
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from datetime import timezone
import configparser
import apprise
import time
import subprocess, signal
import os
import csv
import glob
from influxdb import InfluxDBClient as InfluxDBClientV1
from influxdb_client import InfluxDBClient as InfluxDBClientV2
from influxdb_client.client.write_api import SYNCHRONOUS
try:
    from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("Prometheus client not available. Install with: pip install prometheus_client")

config = configparser.ConfigParser(allow_no_value=True)
db_client = None
buckets_api = None
try:
    config.read("/usr/src/app/config/config.cfg")

    if config.has_section("Measurement"):
        print("Measurement config found")
        MIN_UPLOAD = config.get("Measurement", "min-upload")
        MIN_DOWNLOAD = config.get("Measurement", "min-download")

    if config.has_section("Telegram"):
        print("Telegram config found")
        TELEGRAM_TOKEN = config.get("Telegram", "token")
        TELEGRAM_ID = config.get("Telegram", "ID")

    if config.has_section("MAIL"):
        print("Mail config found")
        MAILUSER = config.get("MAIL", "username")
        MAILDOMAIN = config.get("MAIL", "maildomain")
        MAILPASSWORD = config.get("MAIL", "password")
        MAILTO = config.get("MAIL", "mailto")

    if config.has_section("Twitter"):
        print("Twitter config found")
        TWITTERCKey = config.get("Twitter", "consumerkey")
        TWITTERCSecret = config.get("Twitter", "consumersecret")
        TWITTERAKey = config.get("Twitter", "accesstoken")
        TWITTERASecret = config.get("Twitter", "accesssecret")

    if config.has_section("influxdb"):
        INFLUXDB_HOST = config.get("influxdb", "host")
        INFLUXDB_PORT = config.get("influxdb", "port")
        INFLUXDB_DBNAME = config.get("influxdb", "dbname")
        db_client = InfluxDBClientV1(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
        if not INFLUXDB_DBNAME in db_client.get_list_database():
            db_client.create_database(INFLUXDB_DBNAME)
        db_client.switch_database(INFLUXDB_DBNAME)

    if config.has_section("influxdbv2"):
        print("InfluxDB v2 config found")
        INFLUXDB_HOST = config.get("influxdbv2", "host")
        INFLUXDB_PORT = config.get("influxdbv2", "port")
        INFLUXDB_DBNAME = config.get("influxdbv2", "dbname")
        INFLUXDB_ORG = config.get("influxdbv2", "orgname")
        INFLUXDB_TOKEN = config.get("influxdbv2", "token")
        INFLUXDB_URL = 'http://' + INFLUXDB_HOST + ':' + INFLUXDB_PORT
        with InfluxDBClientV2(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
            buckets_api = client.buckets_api()
            if buckets_api.find_bucket_by_name(INFLUXDB_DBNAME) == None:
                buckets_api.create_bucket(bucket_name=INFLUXDB_DBNAME,
                                            org=INFLUXDB_ORG)

    if config.has_section("prometheus") and PROMETHEUS_AVAILABLE:
        print("Prometheus config found")
        PROMETHEUS_GATEWAY = config.get("prometheus", "gateway")
        PROMETHEUS_JOB = config.get("prometheus", "job", fallback="breitbandmessung")
        PROMETHEUS_INSTANCE = config.get("prometheus", "instance", fallback="default")
                                            
except IOError:
    print("No configuration available", flush=True)


TEST_URL = "https://breitbandmessung.de/test"
FIREFOX_PATH = "firefox-esr"
DOWNLOADED_PATH = "/export/"
SLEEPTIME = 10
SCREENSHOTNAME = "Breitbandmessung_"
SCREENSHOTTEXT = ".png"
GECKODRIVER_PATH = "/usr/bin/geckodriver"


# Ensure export directory exists
if not os.path.exists(DOWNLOADED_PATH):
    try:
        os.makedirs(DOWNLOADED_PATH, exist_ok=True)
        print(f"Created export directory: {DOWNLOADED_PATH}", flush=True)
    except Exception as e:
        print(f"Failed to create export directory {DOWNLOADED_PATH}: {e}", flush=True)
        exit(1)
else:
    print(f"Export directory exists: {DOWNLOADED_PATH}", flush=True)

# Buttons to click
allow_necessary = "#allow-necessary"
start_test_button = "button.btn:nth-child(4)"
allow = "button.btn:nth-child(2)"
website_header = "#root > div > div > div > div > div:nth-child(1) > h1"
download_result = "button.px-0:nth-child(1)"

def cleanup_firefox_profiles():
    """Clean up old Firefox profiles in /tmp to prevent disk space issues"""
    try:
        import glob
        import shutil
        
        # Find all rust_mozprofile* directories in /tmp
        profile_dirs = glob.glob('/tmp/rust_mozprofile*')
        
        if profile_dirs:
            print(f"Found {len(profile_dirs)} Firefox profile directories to clean up", flush=True)
            for profile_dir in profile_dirs:
                try:
                    shutil.rmtree(profile_dir)
                    print(f"Removed Firefox profile: {profile_dir}", flush=True)
                except Exception as e:
                    print(f"Failed to remove Firefox profile {profile_dir}: {e}", flush=True)
        else:
            print("No Firefox profiles found to clean up", flush=True)
    except Exception as e:
        print(f"Error during Firefox profile cleanup: {e}", flush=True)

def closebrowser():
    # Get all running processes
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    # Check from each process and terminate if it is an old Speedtest run
    for line in out.splitlines():
        if FIREFOX_PATH.encode() in line:
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)
    
    # Clean up Firefox profiles after closing browser
    cleanup_firefox_profiles()

# Open browser and testpage breitbandmessung.de/test
print()
print("Open Browser", flush=True)
fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.headless = True
fireFoxOptions.set_preference("browser.download.folderList", 2)
fireFoxOptions.set_preference("browser.download.manager.showWhenStarting", False)
fireFoxOptions.set_preference("browser.download.dir", DOWNLOADED_PATH)
fireFoxOptions.binary_location = FIREFOX_PATH
fireFoxOptions.set_preference(
    "browser.helperApps.neverAsk.saveToDisk", "application/force-download"
)
fireFoxOptions.set_preference("browser.download.panel.shown", False)
# Create Firefox service with geckodriver path
firefox_service = Service(executable_path=GECKODRIVER_PATH)
browser = webdriver.Firefox(service=firefox_service, options=fireFoxOptions)

browser.get(TEST_URL)
print("Click all buttons", flush=True)
accept_necessary_cookies = browser.find_element(By.CSS_SELECTOR, allow_necessary)
try:
    elem = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, allow_necessary))
    )
finally:
    browser.find_element(By.CSS_SELECTOR, allow_necessary)
accept_necessary_cookies = browser.find_element(By.CSS_SELECTOR, allow_necessary)
accept_necessary_cookies.click()

print("Wait until the location window disappears", flush=True)
time.sleep(SLEEPTIME)
try:
    elem = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, start_test_button))
    )
finally:
    browser.find_element(By.CSS_SELECTOR, start_test_button)
print("Clicking the last buttons", flush=True)
start_test_button = browser.find_element(By.CSS_SELECTOR, start_test_button)
start_test_button.click()

data_guidlines = browser.find_element(By.CSS_SELECTOR, allow)
data_guidlines.click()

print("Start measurement", flush=True)
while True:
    try:
        header = browser.find_element(By.CSS_SELECTOR, website_header)
        if "abgeschlossen" in header.text:
            save_result = browser.find_element(By.CSS_SELECTOR, download_result)
            save_result.click()
            
            # Wait for CSV download to complete and then read the data
            time.sleep(3)  # Wait for download to complete
            
            # Find the most recent CSV file in the download directory
            csv_files = glob.glob(os.path.join(DOWNLOADED_PATH, "*.csv"))
            if not csv_files:
                raise FileNotFoundError("No CSV file found in download directory")
            
            # Get the most recent CSV file
            latest_csv = max(csv_files, key=os.path.getctime)
            csv_filename = os.path.basename(latest_csv)
            #print(f"Reading CSV file: {csv_filename}", flush=True)
            
            # Read the CSV file and extract measurement data
            with open(latest_csv, 'r', encoding='utf-8') as file:
                # Use semicolon as delimiter based on the provided format
                csv_reader = csv.DictReader(file, delimiter=';')
                
                # Read the first (and likely only) data row
                data_row = next(csv_reader)
                
                # Extract the values from the CSV
                download_value = data_row['Download (Mbit/s)'].replace(',', '.')  # Convert German decimal format
                upload_value = data_row['Upload (Mbit/s)'].replace(',', '.')
                ping_value = data_row['Laufzeit (ms)']
                
                # Create mock objects that mimic the selenium element behavior
                class MockElement:
                    def __init__(self, text):
                        self.text = text
                
                result_down = MockElement(download_value)
                result_down_unit = MockElement('Mbit/s')
                result_up = MockElement(upload_value)
                result_up_unit = MockElement('Mbit/s')
                result_ping = MockElement(ping_value)
                result_ping_unit = MockElement('ms')
            
            print("", flush=True)
            print("Ping: ", result_ping.text, result_ping_unit.text, flush=True)
            print("Download: ", result_down.text, result_down_unit.text, flush=True)
            print("Upload: ", result_up.text, result_up_unit.text, flush=True)
            now = datetime.now()
            current_time = now.strftime("%H_%M_%S")
            current_date = now.strftime("%d_%m_%Y")
            filename = (
                DOWNLOADED_PATH
                + SCREENSHOTNAME
                + current_date
                + "_"
                + current_time
                + SCREENSHOTTEXT
            )
            browser.save_screenshot(filename)
            if buckets_api or db_client:
                json_body = [
                    {
                        "measurement": "download",
                        "time": now.astimezone(tz=timezone.utc),
                        "fields": {
                            "value": float(result_down.text.replace(",", ".")),
                            "unit": result_down_unit.text,
                        },
                    },
                    {
                        "measurement": "upload",
                        "time": now.astimezone(tz=timezone.utc),
                        "fields": {
                            "value": float(result_up.text.replace(",", ".")),
                            "unit": result_up_unit.text,
                        },
                    },
                    {
                        "measurement": "ping",
                        "time": now.astimezone(tz=timezone.utc),
                        "fields": {
                            "value": int(result_ping.text),
                            "unit": result_ping_unit.text,
                        },
                    },
                ]
                if db_client:
                    db_client.write_points(json_body)
                    db_client.close()
                
                if buckets_api:
                    with InfluxDBClientV2(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
                        write_api = client.write_api(write_options=SYNCHRONOUS)
                        datasave = write_api.write(INFLUXDB_DBNAME, INFLUXDB_ORG, json_body)
            
            # Push metrics to Prometheus if configured
            try:
                if 'PROMETHEUS_GATEWAY' in locals() and PROMETHEUS_AVAILABLE:
                    print("Pushing metrics to Prometheus", flush=True)
                    registry = CollectorRegistry()
                    
                    # Create gauges for metrics
                    download_gauge = Gauge('breitbandmessung_download_mbps', 'Download speed in Mbps', registry=registry)
                    upload_gauge = Gauge('breitbandmessung_upload_mbps', 'Upload speed in Mbps', registry=registry)
                    ping_gauge = Gauge('breitbandmessung_ping_ms', 'Ping in milliseconds', registry=registry)
                    
                    # Set values
                    download_gauge.set(float(result_down.text.replace(",", ".")))
                    upload_gauge.set(float(result_up.text.replace(",", ".")))
                    ping_gauge.set(int(result_ping.text))
                    
                    # Push to gateway
                    push_to_gateway(PROMETHEUS_GATEWAY, job=PROMETHEUS_JOB, registry=registry, 
                                  grouping_key={'instance': PROMETHEUS_INSTANCE})
                    print("Metrics pushed to Prometheus successfully", flush=True)
            except Exception as e:
                print(f"Failed to push metrics to Prometheus: {e}", flush=True)
            
            break
    except:
        now = datetime.now()
        current_time = now.strftime("%H_%M_%S")
        current_date = now.strftime("%d_%m_%Y")
        filename = (
            DOWNLOADED_PATH
            + SCREENSHOTNAME
            + current_date
            + "_error_"
            + current_time
            + SCREENSHOTTEXT
        )
        browser.save_screenshot(filename)  
    finally:
        time.sleep(SLEEPTIME)

try:
    MIN_UPLOAD and MIN_DOWNLOAD
except NameError:
    closebrowser()
    exit()
else:
    # Convert strings to float for proper numerical comparison
    upload_speed = float(result_up.text.replace(",", "."))
    download_speed = float(result_down.text.replace(",", "."))
    min_upload = float(MIN_UPLOAD)
    min_download = float(MIN_DOWNLOAD)
    
    if upload_speed < min_upload or download_speed < min_download:
        internet_to_slow = True
        print("Internet too slow", flush=True)
    else:
        internet_to_slow = False
        print("Internet ok", flush=True)

if internet_to_slow:
    print("Internet to slow", flush=True)
    my_message = (
        "Current Download is: "
        + result_down.text
        + " "
        + result_down_unit.text
        + " and current upload is: "
        + result_up.text
        + " "
        + result_up_unit.text
    )

    apobj = apprise.Apprise()
    config = apprise.AppriseConfig()
    try:
        TELEGRAM_TOKEN and TELEGRAM_TOKEN
        apobj.add("tgram://" + TELEGRAM_TOKEN + "/" + TELEGRAM_ID)
    except NameError:
        print('Telegram not set')
    try:
        MAILUSER and MAILPASSWORD and MAILDOMAIN and MAILTO and MAILUSER
        apobj.add(
            "mailto://"
            + MAILUSER
            + ":"
            + MAILPASSWORD
            + "@"
            + MAILDOMAIN
            + "?to="
            + MAILTO
            + "?from="
            + MAILUSER
            + "&name=Breitbandmessung Docker"
            )
    except NameError:
        print('Mail not set')
    try:
        TWITTERCKey and TWITTERCSecret and TWITTERAKey and TWITTERASecret
        apobj.add(
            "twitter://"
            + TWITTERCKey
            + "/"
            + TWITTERCSecret
            + "/"
            + TWITTERAKey
            + "/"
            + TWITTERASecret
            + "?mode=tweet"
        )
    except NameError:
        print('Twitter not set')

    apobj.notify(
        body=my_message,
        title="Breitbandmessung.de Ergebnis",
        attach=filename,
    )

browser.quit()
closebrowser()
exit()
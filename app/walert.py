#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import paho.mqtt.client as mqtt
import urllib3
import os
import requests
import re
from loguru import logger
import time
import codecs
import apprise
import json
from whatsapp_api_client_python import API

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'C.UTF-8'

debug = os.getenv('DEBUG_MODE')
region = os.getenv('REGION')
INCLUDE_TEST_ALERTS = os.getenv("INCLUDE_TEST_ALERTS")
GREEN_API_INSTANCE = os.getenv("GREEN_API_INSTANCE")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
# reader = codecs.getreader('utf-8')

logger.info("Monitoring alerts for :" + region)


#Setting Request Headers
http = urllib3.PoolManager()
_headers = {'Referer':'https://www.oref.org.il/','User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",'X-Requested-With':'XMLHttpRequest'}
url= 'https://www.oref.org.il/WarningMessages/alert/alerts.json'
if debug == 'True':
   url = 'http://localhost/alerts.json'


alerts = [0]

def alarm_on(data):
    wapp_title = ""#f"*{str(data["title"])}*"
    categorized_places = categorize_places(lamas, data["data"])
    places = format_output(categorized_places)
    body='באזורים הבאים: \r\n ' + places
    try:
        if GREEN_API_INSTANCE and GREEN_API_TOKEN:
            greenAPI = API.GreenAPI(GREEN_API_INSTANCE, GREEN_API_TOKEN)
            greenAPI.sending.sendMessage(WHATSAPP_NUMBER,wapp_title + "\r\n" + body)
    except Exception as e:
        logger.error(f"Error sending whatsapp message. \n {str(e)}")


def is_test_alert(alert):
    # if includes, all alerts are treated as not test
    return INCLUDE_TEST_ALERTS == 'False' and ('בדיקה' in alert['data'] or 'בדיקה מחזורית' in alert['data'])


def standardize_name(name):
    return re.sub(r'[\(\)\'\"]+', '', name).strip()

def load_lamas_data():
    file_path = 'lamas.json'
    github_url = "https://raw.githubusercontent.com/idodov/RedAlert/main/apps/red_alerts_israel/lamas.json"

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lamas_data = json.load(file)
        logger.info("Lamas data loaded from local file")

    except FileNotFoundError:
        logger.error(f"Error: Lamas data file not found at {file_path}, attempting to download from GitHub")
        lamas_data = download_lamas_data(github_url, file_path)

    except json.JSONDecodeError:
        logger.error("Error: Invalid JSON in Lamas data file, attempting to download from GitHub")
        lamas_data = download_lamas_data(github_url, file_path)

    except Exception as e:
        logger.error(f"Error loading Lamas data from local file: {e}")
        lamas_data = download_lamas_data(github_url, file_path)

    if 'areas' not in lamas_data:
        logger.error("Unexpected JSON structure in Lamas data")
        return None

    for area, cities in lamas_data['areas'].items():
        if isinstance(cities, dict):
            standardized_cities = set([
                standardize_name(city) for city in cities.keys()
            ])
        else:
            logger.error(f"Unexpected cities structure in area {area}: {cities}")
            standardized_cities = set()

        lamas_data['areas'][area] = standardized_cities

    return lamas_data

def download_lamas_data(url, file_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        lamas_data = response.json()
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(lamas_data, file, ensure_ascii=False, indent=2)
        logger.info(f"Lamas data downloaded from GitHub and saved to {file_path}")
        return lamas_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading Lamas data from GitHub: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding Lamas data from GitHub: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def categorize_places(data, places):
    categorized_places = {}
    
    for place in places:
        place.replace('"',"''")
        for area, area_places in data['areas'].items():
            if place in area_places:
                if area not in categorized_places:
                    categorized_places[area] = []
                categorized_places[area].append(place)
                break
    
    return categorized_places

def format_output(categorized_places):
    result = []
    for area, places in categorized_places.items():
        result.append(f"*ישובי {area}*:")
        for place in places:
            result.append(place)
    return "\r\n".join(result)


def monitor():
  #start the timer
  threading.Timer(1, monitor).start()
  #Check if data contains alert data
  try:
      r = http.request('GET',url,headers=_headers)
      r.encoding = 'utf-8'
      alert_data = r.data.decode('utf-8-sig').strip("/n").strip()
      if alert_data != '':
          alert = json.loads(alert_data)
          if region in alert["data"] or region=="*":
              if alert["id"] not in alerts and not is_test_alert(alert):
                  alerts.append(alert["id"])
                  alarm_on(alert)
                  logger.info(str(alert))
  except Exception as ex:
         logger.error(str(ex))
  finally:
     r.release_conn()

if __name__ == '__main__':
    lamas = load_lamas_data()
    monitor()
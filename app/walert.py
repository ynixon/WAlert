#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import urllib3
import os
import requests
import re
from loguru import logger
import time
import codecs
import json
from whatsapp_api_client_python import API
from dotenv import load_dotenv
from http.server import HTTPServer, SimpleHTTPRequestHandler

load_dotenv()

# Set encoding environment variables
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "C.UTF-8"

debug = os.getenv("DEBUG_MODE")
region = os.getenv("REGION")
INCLUDE_TEST_ALERTS = os.getenv("INCLUDE_TEST_ALERTS")
GREEN_API_INSTANCE = os.getenv("GREEN_API_INSTANCE")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
# reader = codecs.getreader('utf-8')

if not GREEN_API_TOKEN:
    logger.error("GREEN_API_TOKEN is not set. Please provide it securely at runtime.")
    exit(1)  # Exit if token is missing

logger.info(f"Monitoring alerts for: {region}")

# Setting Request Headers
http = urllib3.PoolManager()
_headers = {
    "Referer": "https://www.oref.org.il/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}
url = "https://www.oref.org.il/WarningMessages/alert/alerts.json"
if debug == "True":
    url = "http://localhost/alerts.json"

MAX_ALERTS = 1000  # Adjust based on expected alert volume
alerts = []  # List to store processed alert IDs

def check_dns():
    try:
        requests.get("https://www.oref.org.il", timeout=5)
        logger.info("DNS resolution successful")
    except requests.exceptions.RequestException as e:
        logger.error(f"DNS resolution error: {e}")


def fetch_alert_data():
    retries = 0
    max_delay = 300  # Maximum wait time between retries (e.g., 5 minutes)
    
    while True:
        try:
            r = http.request("GET", url, headers=_headers)
            if r.status == 200:
                retries = 0  # Reset retries on success
                return r.data.decode("utf-8-sig").strip()
            else:
                logger.error(f"Failed to fetch alert data: HTTP status {r.status}")
        except Exception as e:
            logger.error(f"Error fetching alert data: {e}")
            retries += 1
            
            # Log an additional message every 10 retries
            if retries % 10 == 0:
                logger.warning("Connection issues persisting; continuing retries.")

        # Exponential backoff, capped at `max_delay` seconds
        wait_time = min(10 * (2 ** (retries - 1)), max_delay)
        logger.info(f"Retrying in {wait_time} seconds...")
        time.sleep(wait_time)


def add_alert_id(alert_id):
    if len(alerts) >= MAX_ALERTS:
        alerts.pop(0)  # Remove oldest ID if limit reached
    alerts.append(alert_id)


def start_local_server():
    """Start a local HTTP server to serve alerts.json for debug mode."""
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(("localhost", 8000), handler)
    logger.info("Starting local server for alerts.json at http://localhost:8000")
    threading.Thread(target=httpd.serve_forever, daemon=True).start()


def alarm_on(data):
    title = sanitize_text(str(data["title"]))
    wapp_title = f"*{title}*"
    categorized_places = categorize_places(lamas, data["data"])
    places = format_output(categorized_places)
    body = "באזורים הבאים: \r\n " + places
    try:
        if GREEN_API_INSTANCE and GREEN_API_TOKEN:
            greenAPI = API.GreenAPI(GREEN_API_INSTANCE, GREEN_API_TOKEN)
            message = wapp_title + "\r\n" + body
            logger.info(f"Final WhatsApp message to be sent: {message}")
            greenAPI.sending.sendMessage(WHATSAPP_NUMBER, message)
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")


def is_test_alert(alert):
    # Return True if it's a test alert and we exclude test alerts
    return INCLUDE_TEST_ALERTS == "False" and (
        "בדיקה" in alert["data"] or "בדיקה מחזורית" in alert["data"]
    )


def sanitize_text(text):
    # Replace all apostrophe variants with a single character
    return text.replace("׳", "'").replace("’", "'").replace("`", "'").strip()


def standardize_name(name):
    return re.sub(r"[\(\)\'\"\׳`’]+", "'", name).strip()


def load_lamas_data():
    file_path = "lamas.json"
    github_url = "https://raw.githubusercontent.com/idodov/RedAlert/main/apps/red_alerts_israel/lamas.json"
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lamas_data = json.load(file)
        logger.info("Lamas data loaded from local file")
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("Lamas data file not found or invalid; downloading from GitHub")
        lamas_data = download_lamas_data(github_url, file_path)

    if "areas" not in lamas_data:
        logger.error("Unexpected JSON structure in Lamas data")
        return None

    for area, cities in lamas_data["areas"].items():
        if isinstance(cities, dict):
            standardized_cities = {standardize_name(city) for city in cities.keys()}
        else:
            logger.error(f"Unexpected structure in area {area}: {cities}")
            standardized_cities = set()
        lamas_data["areas"][area] = standardized_cities

    return lamas_data


def download_lamas_data(url, file_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        lamas_data = response.json()
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(lamas_data, file, ensure_ascii=False, indent=2)
        logger.info(f"Lamas data downloaded from GitHub and saved to {file_path}")
        return lamas_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading Lamas data from GitHub: {e}")
        return None


def categorize_places(data, places):
    categorized_places = {}
    for place in places:
        place = sanitize_text(place)
        logger.info(f"Processing place: {place}")
        matched = False
        for area, area_places in data["areas"].items():
            if place in area_places:
                categorized_places.setdefault(area, []).append(place)
                matched = True
                break
        if not matched:
            logger.warning(f"Place '{place}' did not match any area in lamas data.")
    return categorized_places


def format_output(categorized_places):
    result = []
    for area, places in categorized_places.items():
        result.append(f"*ישובי {sanitize_text(area)}*:")
        result.extend(sanitize_text(place) for place in places)
    final_output = "\r\n".join(result)
    logger.info(f"Formatted output for WhatsApp: {final_output}")
    return final_output


def monitor():
    # Start the timer to re-run monitor every second
    threading.Timer(1, monitor).start()
    try:
        # Load alert data from file in debug mode, otherwise fetch from the URL
        if debug == "True":
            with open("alerts.json", "r", encoding="utf-8") as f:
                alert = json.load(f)
        else:
            

            # Fetch alert data with retry logic
            alert_data = fetch_alert_data()

            if not alert_data:
                #logger.warning("No alert data received, skipping processing.")
                return  # Skip further processing if alert data is missing

            try:
                # Parse JSON data
                alert = json.loads(alert_data)
            except json.JSONDecodeError as ex:
                logger.error(f"JSON Decode Error in monitor: {ex} - Data received: {alert_data}")
                return  # Skip further processing if JSON decoding fails

        # Check if the alert is relevant and hasn't been processed already
        if alert and (region in alert["data"] or region == "*"):
            logger.info(f"Alert data: {alert['data']}, Region: {region}")
            if alert["id"] not in alerts and not is_test_alert(alert):
                add_alert_id(alert["id"])
                alarm_on(alert)
                logger.info(f"Processed alert: {alert}")

    except Exception as ex:
        logger.error(f"Error in monitor: {ex}")

# Ensure to initialize and start the monitor loop
if __name__ == "__main__":
    check_dns()  # Check DNS resolution before starting
    if debug == "True":
        start_local_server()
    lamas = load_lamas_data()
    monitor()


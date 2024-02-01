import requests
import time
import json
import engine.config as config
from datetime import datetime


def image_download(url):
    if not url:
        return None, None
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        content_type = response.headers['Content-Type']
        if 'image/jpeg' in content_type:
            extension = '.jpg'
        elif 'image/png' in content_type:
            extension = '.png'
        elif 'image/gif' in content_type:
            extension = '.gif'
        else:
            return None, None
        image_binary_data = response.content
        current_unix_time = int(time.time())
        image_filename = f'{current_unix_time}{extension}'
        return image_binary_data, image_filename
    except requests.exceptions.RequestException:
        return None, None


def save_image_file(image_binary_data):
    with open(config.INTRODUCTION_IMAGE_FILEPATH, 'wb') as file:
        file.write(image_binary_data)


def load_event_settings():
    try:
        with open(config.EVENT_SETTINGS, 'r') as file:
            event_settings = json.load(file)
            return event_settings
    except FileNotFoundError:
        return None


def save_event_settings(event_settings):
    with open(config.EVENT_SETTINGS, 'w') as settings:
        json.dump(event_settings, settings, indent=4, ensure_ascii=False)


def get_parsed_date(given_date):
    try:
        date_obj = datetime.strptime(given_date, '%d.%m.%Y')
        current_date = datetime.now().date()
        if date_obj.date() > current_date:
            return {
                "day": date_obj.day,
                "month": date_obj.month,
                "year": date_obj.year
            }
    except ValueError:
        return False

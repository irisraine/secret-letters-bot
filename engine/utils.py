import requests
import time
import os


def image_download(url):
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
            return False
        current_unix_time = int(time.time())
        filename = os.path.join('database/postcards', f'{current_unix_time}{extension}')
        with open(filename, 'wb') as file:
            file.write(response.content)
        return filename
    except requests.exceptions.RequestException:
        return False

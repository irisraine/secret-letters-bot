import requests
import time


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
            return None, None
        image_binary_data = response.content
        current_unix_time = int(time.time())
        image_filename = f'{current_unix_time}{extension}'
        return image_binary_data, image_filename
    except requests.exceptions.RequestException:
        return None, None

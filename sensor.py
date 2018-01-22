from pprint import pprint
import os
import sys
import time
import json
from dotenv import load_dotenv

from ds18b20 import DS18B20
from gituploader import GitUploader

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
__data_dir__ = os.path.join(__location__, 'data')

load_dotenv(os.path.join(__location__, '.env'))

sensor = DS18B20()
t = sensor.temperature()

if not t:
    sys.exit("Temperature was not found")

def update_data(t):
    t_direction = 0
    file_24_path = os.path.join(__data_dir__, 'temperature_24.json')
    file_now_path = os.path.join(__data_dir__, 'temperature_now.json')

    try:
        file_24 = open(file_24_path)
        json_data = json.load(file_24)
        file_24.close()
    except:
        json_data = []

    if json_data:
        until_time = int(time.time()) - 86400
        prev_t = json_data[-1]['t']

        # Get new temperature direction
        if prev_t < t:
            t_direction = 1
        elif prev_t > t:
            t_direction = -1

        # Remove old data
        for (i, item) in enumerate(json_data):
            if item['time'] <= until_time:
                json_data.pop(i)
            else:
                break

    new_data = {
        'time': int(time.time()),
        't': t
    }
    json_data.append(new_data)

    file_24 = open(file_24_path, 'w')
    if file_24.write(json.dumps(json_data, sort_keys=False)):
        file_24.close()

    new_data['direction'] = t_direction

    file_now = open(file_now_path, 'w')
    if file_now.write(json.dumps(new_data, sort_keys=False)):
        file_now.close()

    return True

if update_data(t):
    git_uploader = GitUploader(__data_dir__)
    git_uploader.commit()

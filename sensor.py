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


def save_data(t):
    file_path = os.path.join(__data_dir__, 'temperature.json')

    json_data = json.dumps({
        'time': int(time.time()),
        't': t
    })

    file = open(file_path, 'w')
    if file.write(json_data):
        return file_path

file_path = save_data(t)

git_uploader = GitUploader(__data_dir__)
git_uploader.commit()
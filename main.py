#!/usr/bin/env python3

import os
import json
import datetime
from dotenv import load_dotenv
from gitpusher import GitPusher
from pprint import pprint
import darksky
load_dotenv()

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
__data_dir__ = os.path.join(__location__, 'data')


if os.getenv("EMULATION_MODE") == "True":
    from emulation import W1ThermSensor, bme280
else:
    from smbus2 import SMBus
    from bme280 import BME280
    from w1thermsensor import W1ThermSensor

    bus = SMBus(0)
    bme280 = BME280(i2c_dev=bus)
    bme280.setup(mode="forced")

w1Therm = W1ThermSensor()


def get_sensors_data() -> dict:
    result = {
        'w1_t': w1Therm.get_temperature(),
        'bme280_t': bme280.get_temperature(),
        'bme280_p': 0.750061 * bme280.get_pressure(),  # Convert hPa to mercurial
        'bme280_h': bme280.get_humidity()
    }
    for key, value in result.items():
        result[key] = round(value, 2)

    return result

def get_forecast():
    result = None
    try:
        forecast = darksky.forecast(os.getenv("DARKSKY_KEY"), os.getenv("DARKSKY_LAT"), os.getenv("DARKSKY_LONG"), None, None, lang="ru", units="si", exclude="minutely,hourly,alerts")
    except Exception as e:
        print(str(e))
        return result

    result = {
        'now_summary':      forecast.currently.summary,
        'now_icon':         forecast.currently.icon,
        'now_temperature':  forecast.currently.temperature,
        'now_humidity':     forecast.currently.humidity,
        'now_pressure':     round(0.750061 * forecast.currently.pressure, 2),
        'now_windSpeed':    forecast.currently.windSpeed,

        'today_summary':    forecast.daily.summary,
        'today_icon':       forecast.daily.icon,

        'tomorrow_summary':         forecast.daily.data[1].summary,
        'tomorrow_icon':            forecast.daily.data[1].icon,
        'tomorrow_temperatureMax':  forecast.daily.data[1].temperatureMax,
        'tomorrow_temperatureMin':  forecast.daily.data[1].temperatureMin,
        'tomorrow_humidity':        forecast.daily.data[1].humidity,
        'tomorrow_pressure':        round(0.750061 * forecast.daily.data[1].pressure, 2),
        'tomorrow_windSpeed':       forecast.daily.data[1].windSpeed,
    }

    try:
        result['now_precipType'] = forecast.currently.precipType
    except:
        result['now_precipType'] = None

    try:
        result['tomorrow_precipType'] = forecast.daily.data[1].precipType
    except:
        result['tomorrow_precipType'] = None

    return result

def store_data(sensors_data):
    forecast = get_forecast()

    now = datetime.datetime.now()
    temp_direction = 0
    file_24_path = os.path.join(__data_dir__, 'temperature_24.json')
    file_now_path = os.path.join(__data_dir__, 'temperature_now.json')

    try:
        file_24 = open(file_24_path, encoding="utf-8")
        file_24_json = json.load(file_24)
        file_24.close()
    except:
        file_24_json = []

    # if file exists
    if file_24_json:
        until_time = int(now.timestamp()) - 86400   # 24 hours

        # Get new temperature direction
        prev_temp = file_24_json[-1]['w1_t']
        if prev_temp < sensors_data['w1_t']:
            temp_direction = 1
        elif prev_temp > sensors_data['w1_t']:
            temp_direction = -1

        # Remove old data
        for (i, item) in enumerate(file_24_json):
            if item['time'] <= until_time:
                file_24_json.pop(i)
            else:
                break

    ''' 
    24 HOURS FILE
    '''
    sensors_data['fc_t'] = forecast['now_temperature']
    sensors_data['fc_h'] = forecast['now_humidity']
    sensors_data['fc_p'] = forecast['now_pressure']

    sensors_data['time'] = int(now.timestamp())
    file_24_json.append(sensors_data)

    file_24 = open(file_24_path, 'w', encoding="utf-8")
    if file_24.write(json.dumps(file_24_json, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))):
        file_24.close()

    ''' 
    CURRENT OR NOW DATA FILE
    '''
    sensors_data['temp_direction'] = temp_direction
    sensors_data['forecast'] = forecast
    file_now = open(file_now_path, 'w', encoding="utf-8")
    if file_now.write(json.dumps(sensors_data, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))):
        file_now.close()

    return True

def main():
    sensors_data = get_sensors_data()
    store_data(sensors_data)
    git = GitPusher(__data_dir__)
    git.commit()

if __name__ == "__main__":
    main()

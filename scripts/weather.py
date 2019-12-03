#!/usr/bin/env python3

import requests
import sys
import json
import os

# def download_sunrise_sunset():
#     payload = {"lat": 51.416039, "lng": -0.753980, "formatted": 0,}
#     result = requests.get("https://api.sunrise-sunset.org/json",
#         params = payload)
#     result.raise_for_status() # Throws if something went wrong
#     result = result.json()["results"]

# result = """{"current": {"cloudcover": 37, "weather_descriptions": ["Partly cloudy"], "uv_index": 0, "wind_speed": 19, "weather_icons": ["https://assets.weatherstack.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"], "temperature": 6, "visibility": 10, "wind_dir": "NNE", "wind_degree": 14, "is_day": "no", "precip": 0, "feelslike": 2, "humidity": 76, "weather_code": 116, "observation_time": "05:08 PM", "pressure": 1024}, "location": {"name": "Priestwood", "lat": "51.418", "timezone_id": "Europe/London", "lon": "-0.758", "localtime_epoch": 1575220080, "country": "United Kingdom", "region": "Berkshire", "localtime": "2019-12-01 17:08", "utc_offset": "0.0"}, "request": {"unit": "m", "language": "en", "type": "LatLon", "query": "Lat 51.42 and Lon -0.75"}}
# """

def download_temperature_now_from_weatherstack(weatherstack_api_key):
    #TODO: move this to another file!

    params = {
        "query": "51.416039, -0.753980",
        "units": "m",
        "access_key": weatherstack_api_key,
    }

    assert(weatherstack_api_key != "".join(["x"] * 26))
    result = requests.get("http://api.weatherstack.com/current", params)
    try:
        result.raise_for_status()
        json_result = result.json()
        # json_result = json.loads(result)
        # return json_result["current"]["temperature"]
        # Feelslike presumably includes wind chill so cooler than outside
        #print(json_result)
        #print(json_result["current"])
        return json_result["current"]["temperature"]
    except:
        print("Made request to weatherstack api, got response: " + str(result))
        raise

# print(download_temperature_now_from_weatherstack())
# print(type(download_temperature_now_from_weatherstack()))
# assert type(download_temperature_now_from_weatherstack()) is int

def read_api_key_from_file(filepath):
    with open("weatherstack_api_key", "r") as f:
        return f.read().rstrip("\n")

def calculate_door_open_time(
    temperature_celsius,
    door_open_min_time_seconds = 40,
    door_open_full_time_seconds = 80,
    door_open_min_temp = 0,
    door_open_max_temp_offset_from_min = 20,
    # door_open_max_temp = door_open_min_temp + 20,
    ):
    door_open_max_temp = door_open_min_temp + door_open_max_temp_offset_from_min

    assert door_open_full_time_seconds > door_open_min_time_seconds
    assert door_open_max_temp_offset_from_min >= 0

    if temperature_celsius <= door_open_min_temp:
        return door_open_min_time_seconds
    elif temperature_celsius >= door_open_max_temp:
        return door_open_full_time_seconds

    proportion = (temperature_celsius /
            (door_open_max_temp - door_open_min_temp))
    extra_time = proportion * (door_open_full_time_seconds - door_open_min_time_seconds)
    # print(proportion)
    # assert 0 < proportion < 1
    # assert extra_time <= (door_open_full_time_seconds - door_open_min_time_seconds)
    return int(door_open_min_time_seconds + extra_time)

# api_response = download_from_weatherstack()

# print(api_response)
# print(api_response)
# for k, v in api_response.items():
#     print(k, v)
# print(u"Current temperature in %s is %d℃" % (api_response["location"]["name"], api_response["current"]["temperature"]))
# def main(argv):
#     print("Hello world!")

if __name__ == "__main__":
    # for i in range(-10, 35):
    #     print(i, calculate_door_open_time(i))
    # sys.exit(main(sys.argv))
    api_key = read_api_key_from_file("weatherstack_api_key")
    temperature_celsius = download_temperature_now_from_weatherstack(api_key)
    door_opening_time_seconds = calculate_door_open_time(temperature_celsius)
    print(door_opening_time_seconds)



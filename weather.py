#!/usr/bin/env python

import urllib3
import json
import geocoder
import sys
import configparser
import os
import pathlib
import sys

# Endpoint to query
url = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric"

class CannotGetError(Exception):
    """ Exception that defines a cannot get"""

def grace_exit(msg = "Could not complete execution, error occurred"):
    """(Void) A function used for graceful exits."""

    print(msg)
    sys.exit(1)

def debug(msg):
    """(Void)Function to be used for debugging"""

    if os.getenv("WEATHER_DEBUG") != None:
        print("DEBUG:", msg)

def parse_conf():
    """(Dictionary) Function that parses the config file and/or environment variables and returns dictionary."""

    # Following tuple holds the configfile/env var versions of each config
    ALL_CONFIGS = (
        # Name of the variable in code, Path to config in the config file(section + value), name of environment variable, default value)
        ("data_store", "default", "path_to_result", "WEATHER_PATH_TO_RESULT", "data"),
        ("geocoder", "default", "geocoder", "WEATHER_GEOCODER", "YES"),
        ("lat", "default", "lat", "WEATHER_LAT", "0"),
        ("lon", "default", "lon", "WEATHER_LON", "0"),
        ("api_key", "credentials", "openweather_api", "")
    )

    # Initialize return dictionary
    ret = {}

    # Attempt to read config file
    path_to_config = os.getenv("WEATHER_CONFIG", "weather.conf")

    config = configparser.ConfigParser()
    config.read(path_to_config)
    debug("Config sections loaded: " + str(config.sections()))

    for t in ALL_CONFIGS:
        tmp_env = os.getenv(t[3])
        if tmp_env != None:
            ret[t[0]] = tmp_env
            debug("Environment variable loaded for " + t[0] + " is " + str(tmp_env))
        elif t[1] in config and t[2] in config[t[1]]:
            debug("Config file value loaded for " + t[0] + " is " + config[t[1]][t[2]])
            ret[t[0]] = config[t[1]][t[2]]
        else:
            debug("Couldn't not find a config file value nor Environment variable for " + t[0])
            debug("Default value for " + t[0] + " is " + t[4])
            ret[t[0]] = t[4]

    return ret

def main():

    # Get config
    conf = parse_conf()

    # Get Lat/Lon for weather retrieval
    if conf['geocoder'].lower() != 'no' and conf['geocoder'].lower() != 'false':
        try:
            g = geocoder.ip('me')
        except Exception as e:
            print(e)
        else:
            lat = g.latlng[0]
            lon = g.latlng[1]
    else:
        lat = conf['lat']
        lon = conf['lon']

    # Perform API call
    try:
        pm = urllib3.PoolManager()
        out = pm.request('GET', url.format(lat, lon, conf['api_key']))
        if out.status != 200:
            raise CannotGetError

        res = json.loads(out.data.decode("utf-8"))
    except CannotGetError:
        grace_exit("API call returned HTTP code: " + str(out.status) + "Try again later")

    # Define output string
    weather = ''

    # If answer is meaningful...
    if len(res['weather']) > 1:
        for x in res['weather']:
            weather += x['description'] + " and "
    else:
        weather = res['weather'][0]['description']

    out = "Weather in {} is {}C with {}\n".format(res['name'], res['main']['temp'], weather)

    try:
        with open(conf['data_store'], 'w') as f:
            f.write(out)
    except IOError:
        grace_exit("Could not write to " + conf['data_store'])

if __name__ == "__main__":
    main()

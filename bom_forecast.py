# -*- coding: utf-8 -*-
"""
Created on July 2021

@author: javgarces ()

Sources:
https://gist.github.com/just-digital/2279541
https://stackoverflow.com/questions/2792650/import-error-no-module-name-urllib2
http://www.bom.gov.au/catalogue/data-feeds.shtml#precis
https://stackoverflow.com/questions/20166749/how-to-convert-an-ordereddict-into-a-regular-dict-in-python3
https://github.com/martinblech/xmltodict

"""

import sys
import argparse
import json
from urllib.request import urlopen
import xmltodict

#%% Defining arguments

description = """
Australian Bureau of Meterology Forecasts by State and Location
"""

parser = argparse.ArgumentParser(description=description)
parser.add_argument("--state", type=str, help="Default value: VIC")
parser.add_argument("--location", type=str, help="Default value: Geelong")

args = parser.parse_args()

STATE = args.state
LOCATION = args.location

if not args.state:
    print('\n(use "-h" for usage details)\nUsing default state:\tVIC')
    STATE = "VIC"

#%% Getting the data

def get_file_from_state(state):
    states = [
        "NSW",
        "ACT",
        "NT",
        "QLD",
        "SA",
        "TAS",
        "VIC",
        "WA"
        ]
    files = [
        "ftp://ftp.bom.gov.au/anon/gen/fwo/IDN11060.xml",
        "ftp://ftp.bom.gov.au/anon/gen/fwo/IDN11060.xml",
        "ftp://ftp.bom.gov.au/anon/gen/fwo/IDD10207.xml",
        "ftp://ftp.bom.gov.au/anon/gen/fwo/IDQ11295.xml",
        "ftp://ftp.bom.gov.au/anon/gen/fwo/IDS10044.xml",
        "ftp://ftp.bom.gov.au/anon/gen/fwo/IDT16710.xml",
        "ftp://ftp.bom.gov.au/anon/gen/fwo/IDV10753.xml",
        "ftp://ftp.bom.gov.au/anon/gen/fwo/IDW14199.xml"
        ]
    if state not in states:
        error_msg = "State not recognised\nMust be one of the following: "
        sys.exit(error_msg + ", ".join(states))
    else:
        return files[states.index(state)]
    
def get_data_from_state(state):
    file = get_file_from_state(state)
    response = urlopen(file)
    raw = response.read()    
    foo = xmltodict.parse(raw)        
    data = json.loads(json.dumps(foo))
    return data

data = get_data_from_state(STATE)

#%% Finding data for given LOCATION

def get_location_dict(data):
    location_data = data['product']['forecast']['area']
    location_dict = dict()
    for location_item in location_data:
        location = location_item['@description']
        if 'forecast-period' in location_item:
            location_dict[location] = location_item['forecast-period']
    return location_dict
    
location_dict = get_location_dict(data)

# Handling issues

if not args.state and not args.location:
    print('Using default state:\tGeelong')
    LOCATION = "Geelong"

if args.state and not args.location:
    error_msg = "Location not given\nMust be one of the following: "
    sys.exit(error_msg + ", ".join(sorted(location_dict.keys())))
        
if LOCATION not in location_dict.keys():
    error_msg = "Location {} not found in state {}.\n".format(LOCATION, STATE)
    error_msg += "Must be one of the following: "
    sys.exit(error_msg + ", ".join(sorted(location_dict.keys())))
    
# Print list of forecasts

forecast_prints = list()

for forecast in location_dict[LOCATION]:
    date = forecast['@start-time-local'].split('T')[0]
    forecast_items = list()
    if type(forecast['element']) is not list:
        continue
    for element in forecast['element']:
        if element['@type'] == 'air_temperature_minimum':
            forecast_items.append("Min: {} C".format(element['#text']))
        if element['@type'] == 'air_temperature_maximum':
            forecast_items.append("Max: {} C".format(element['#text']))
    forecast_prints.append("{}: {}".format(date, ", ".join(forecast_items)))

print("\nForecast for {}, {}:\n".format(LOCATION, STATE))

for line in forecast_prints:
    print(line)


#!/usr/bin/env python3

import csv
import gzip
import simplejson as json
import os
import pymongo
import re
from lib import pluralize

def parse_uk(country, basepath):
    stations = { 'train': [], 'bus': [], 'metro': []}
    path = basepath + 'countries/uk/Stops.csv.gz'
    with gzip.open(path, mode='rt', encoding="ISO-8859-1") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == "AtcoCode":
                continue

            station = {}
            station['city'] = row[21]           # Town
            station['station_id'] = row[0]      # AtcoCode
            station['name'] = row[4]            # CommonName

            loc = {}
            loc['type'] = 'Point'
            loc['coordinates'] = [ float(row[29]), float(row[30]) ]
            station['loc'] = loc

            # http://www.naptan.org.uk/schema/2.1/napt/NAPT_stop-v2-1.xsd
            if re.match("BCT|BCS|BCE|BCQ", row[31]):
                station['mode'] = 'bus'
            elif re.match("RSE|RLY", row[31]):
                station['mode'] = 'train'
            elif re.match("TMU|MET|PLT", row[31]):
                station['mode'] = 'metro'
            elif re.match("TXR|STR|FTD|FBT|FER|AIR|GAT", row[31]):
                # currently don't support taxis, ferries, or airports
                continue
            else:
                print("Unrecognized type: ", row[31])

            stations[station['mode']].append(station)

    for m in ['train', 'bus', 'metro']:
        with open(basepath + pluralize(m) + '/' + country + '.json', 'w') as f:
            f.write(json.dumps(stations[m]))

def do_import(mongo_uri, basepath):
    station_parsers = [
        ['UK', parse_uk],
    ]

    for parser in station_parsers:
        stations = parser[1](parser[0], basepath)
        print("Prepared", parser[0], "for import")

if __name__ == "__main__":
    from lib import get_mongo_config, get_basepath
    mongo_uri = get_mongo_config()
    basepath = get_basepath()

    do_import(mongo_uri, basepath)

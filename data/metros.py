#!/usr/bin/env python3

import csv
import simplejson as json
import pymongo
from lxml import etree
from pykml import parser

def parse_london_metro(basepath):
    with open(basepath + 'stations.kml', 'rb') as x:
        xml = etree.parse(x)
    k = parser.fromstring(etree.tostring(xml))
    places = (k.findall('.//{http://www.opengis.net/kml/2.2}Placemark'))

    stations = []
    count = 0
    for p in places:
        station = { 'mode' : 'metro' }
        station['city'] = 'London'
        station['name'] = p.name.text.strip()

        coords = [float(c.strip()) for c in p.Point.coordinates.text.split(',')]

        # London inserts a trailing 0 coordinate too? Why!?
        coords.pop()

        loc = { 'type' : 'Point' }
        loc['coordinates'] = coords
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_uk_metro(basepath):
    json_data = open(basepath + 'UK.json').read()
    data = json.loads(json_data)

    stations = []
    for d in data:
        stations.append(d)

    return stations

def parse_madrid_metro(basepath):
    files = ['Metro.kml', 'MetroLigero.kml']
    places = []
    for f in files:
        with open(basepath + f, 'rb') as x:
            xml = etree.parse(x)
        k = parser.fromstring(etree.tostring(xml))
        places.extend(k.findall('.//{http://www.opengis.net/kml/2.2}Placemark'))

    stations = []
    count = 0
    for p in places:
        station = { 'mode' : 'metro' }
        station['city'] = 'Madrid'
        station['name'] = p.name.text

        coords = [float(c.strip()) for c in p.Point.coordinates.text.split(',')]

        loc = { 'type' : 'Point' }
        loc['coordinates'] = coords
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_bcn_metro(basepath):
    files = ['TMB_EST.kml', 'TRAM_EST.kml']
    places = []
    for f in files:
        with open(basepath + f, 'rb') as x:
            xml = etree.parse(x)
        k = parser.fromstring(etree.tostring(xml))
        places.extend(k.findall('.//{http://www.opengis.net/kml/2.2}Placemark'))

    stations = []
    count = 0
    for p in places:
        station = { 'mode' : 'metro' }
        station['city'] = 'Barcelona'
        station['name'] = p.name.text

        coords = [float(c.strip()) for c in p.Point.coordinates.text.split(',')]

        # BCN inserts a trailing 0 coordinate? Why!?
        coords.pop()

        loc = { 'type' : 'Point' }
        loc['coordinates'] = coords
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_bilbao_metro(basepath):
    with open(basepath + 'stops.txt') as f:
        reader = csv.reader(f, delimiter=',')

        stations = []
        for row in reader:
            if row[0] == "stop_id":
                continue

            station = { 'mode' : 'metro' }
            station['city'] = 'Bilbao'
            station['name'] = row[2]            # stop_name

            loc = { 'type' : 'Point' }
            loc['coordinates'] = [ float(row[4]), float(row[3]) ]
            station['loc'] = loc

            stations.append(station)

    return stations

def do_import(mongo_uri, basepath):
    station_parsers = [
        ['Madrid', parse_madrid_metro],
        ['Barcelona', parse_bcn_metro],
        ['Bilbao', parse_bilbao_metro],
        ['London', parse_london_metro],
        ['UK', parse_uk_metro],
    ]
    client = pymongo.MongoClient(mongo_uri)
    db = client.openmotion
    metros = db.metros

    for parser in station_parsers:
        metros.insert(parser[1](basepath))

    client.disconnect()

if __name__ == "__main__":
    from lib import get_mongo_config, get_basepath, mongo_drop, mongo_index
    mode = 'metros'
    mongo_uri = get_mongo_config()
    basepath = get_basepath() + mode + '/'

    mongo_drop(mongo_uri, mode)
    do_import(mongo_uri, basepath)
    mongo_index(mongo_uri, mode)

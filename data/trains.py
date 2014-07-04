#!/usr/bin/env python3

import csv
import pymongo
from lxml import etree
from pykml import parser
import simplejson as json

def parse_madrid_train(basepath):
    with open(basepath + 'Cercanias.kml', 'rb') as x:
        xml = etree.parse(x)
    k = parser.fromstring(etree.tostring(xml))
    places = (k.findall('.//{http://www.opengis.net/kml/2.2}Placemark'))

    stations = []
    count = 0
    for p in places:
        station = { 'mode' : 'train' }
        station['city'] = 'Madrid'
        station['name'] = p.name.text

        coords = [float(c.strip()) for c in p.Point.coordinates.text.split(',')]

        loc = { 'type' : 'Point' }
        loc['coordinates'] = coords
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_bcn_train(basepath):
    files = ['FGC_EST.kml', 'RENFE_EST.kml']
    places = []
    for f in files:
        with open(basepath + f, 'rb') as x:
            xml = etree.parse(x)
        k = parser.fromstring(etree.tostring(xml))
        places.extend(k.findall('.//{http://www.opengis.net/kml/2.2}Placemark'))

    stations = []
    count = 0
    for p in places:
        station = { 'mode' : 'train' }
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

def parse_zaragoza_train(basepath):
    json_data = open(basepath + 'Paradas_Tranviawgs84.json').read()
    data = json.loads(json_data)

    stations = []
    for d in data['features']:
        station = { 'mode' : 'train' }
        station['city'] = 'Zaragoza'
        station['name'] = d['properties']['NOMBRE']
        station['loc'] = d['geometry']

        stations.append(station)

    return stations

def parse_uk_train(basepath):
    json_data = open(basepath + 'UK.json').read()
    data = json.loads(json_data)

    stations = []
    for d in data:
        stations.append(d)

    return stations

def parse_bilbao_train(basepath):
    with open(basepath + 'stops.txt') as f:
        reader = csv.reader(f, delimiter=',')

        stations = []
        for row in reader:
            if row[0] == "stop_id":
                continue

            station = { 'mode' : 'train' }
            station['city'] = 'Bilbao'
            station['name'] = row[2]            # stop_name

            loc = { 'type' : 'Point' }
            loc['coordinates'] = [ float(row[5]), float(row[4]) ]
            station['loc'] = loc

            stations.append(station)

    return stations

def do_import(mongo_uri, basepath):
    station_parsers = [
        ['Madrid', parse_madrid_train],
        ['Barcelona', parse_bcn_train],
        ['Zaragoza', parse_zaragoza_train],
        ['Bilbao', parse_bilbao_train],
        ['UK', parse_uk_train],
    ]
    client = pymongo.MongoClient(mongo_uri)
    db = client.openmotion
    trains = db.trains

    for parser in station_parsers:
        stations = parser[1](basepath)
        count = 0
        for s in stations:
            res = trains.update({'loc' : s['loc']}, s, upsert=True)

            if res['updatedExisting'] == False:
                count = count + 1
        print(parser[0], "inserted", count, "new records.")

    client.disconnect()

if __name__ == "__main__":
    from lib import get_mongo_config, get_basepath, mongo_drop, mongo_index
    mode = 'trains'
    mongo_uri = get_mongo_config()
    basepath = get_basepath() + mode + '/'

    mongo_drop(mongo_uri, mode)
    do_import(mongo_uri, basepath)
    mongo_index(mongo_uri, mode)

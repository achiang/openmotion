#!/usr/bin/env python3

import csv
import pymongo
from lxml import etree
from pykml import parser
import simplejson as json

def parse_madrid_train(basepath):
    with open(basepath + 'train/Cercanias.kml', 'rb') as x:
        xml = etree.parse(x)
    k = parser.fromstring(etree.tostring(xml))
    places = (k.findall('.//{http://www.opengis.net/kml/2.2}Placemark'))

    stations = []
    count = 0
    for p in places:
        station = {}
        station['city'] = 'Madrid'
        station['name'] = p.name.text

        coords = [float(c.strip()) for c in p.Point.coordinates.text.split(',')]

        loc = {}
        loc['type'] = 'Point'
        loc['coordinates'] = coords
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_bcn_train(basepath):
    files = ['train/FGC_EST.kml', 'train/RENFE_EST.kml']
    places = []
    for f in files:
        with open(basepath + f, 'rb') as x:
            xml = etree.parse(x)
        k = parser.fromstring(etree.tostring(xml))
        places.extend(k.findall('.//{http://www.opengis.net/kml/2.2}Placemark'))

    stations = []
    count = 0
    for p in places:
        station = {}
        station['city'] = 'Barcelona'
        station['name'] = p.name.text

        coords = [float(c.strip()) for c in p.Point.coordinates.text.split(',')]

        # BCN inserts a trailing 0 coordinate? Why!?
        coords.pop()

        loc = {}
        loc['type'] = 'Point'
        loc['coordinates'] = coords
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_zaragoza_train(basepath):
    json_data = open(basepath + 'train/Paradas_Tranviawgs84.json').read()
    data = json.loads(json_data)

    stations = []
    for d in data['features']:
        station = {}
        station['city'] = 'Zaragoza'
        station['name'] = d['properties']['NOMBRE']
        station['loc'] = d['geometry']

        stations.append(station)

    return stations

def parse_bilbao_train(basepath):
    with open(basepath + 'train/stops.txt') as f:
        reader = csv.reader(f, delimiter=',')

        stations = []
        for row in reader:
            if row[0] == "stop_id":
                continue

            station = {}
            station['city'] = 'Bilbao'
            station['name'] = row[2]            # stop_name

            loc = {}
            loc['type'] = 'Point'
            loc['coordinates'] = [ float(row[5]), float(row[4]) ]
            station['loc'] = loc

            stations.append(station)

    return stations

def parse_train(mongo_uri, basepath):
    station_parsers = [
        ['Madrid', parse_madrid_train],
        ['Barcelona', parse_bcn_train],
        ['Zaragoza', parse_zaragoza_train],
        ['Bilbao', parse_bilbao_train],
    ]
    client = pymongo.MongoClient(mongo_uri)
    db = client.openmotion
    train = db.train

    for parser in station_parsers:
        stations = parser[1](basepath)
        count = 0
        for s in stations:
            res = train.update({'loc' : s['loc']}, s, upsert=True)

            if res['updatedExisting'] == False:
                count = count + 1
        print(parser[0], "inserted", count, "new records.")

    client.disconnect()

def drop_and_recreate(mongo_uri):
    client = pymongo.MongoClient(mongo_uri)
    db = client.openmotion
    db.drop_collection('train')
    client.disconnect()

    client = pymongo.MongoClient(mongo_uri)
    db = client.openmotion
    db.train.ensure_index([('loc', pymongo.GEOSPHERE)])
    client.disconnect()

if __name__ == "__main__":
    from lib import get_mongo_config, get_basepath
    mongo_uri = get_mongo_config()
    basepath = get_basepath()

    drop_and_recreate(mongo_uri)
    parse_train(mongo_uri, basepath)

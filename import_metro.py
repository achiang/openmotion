#!/usr/bin/env python3

import csv
import pymongo
from lxml import etree
from pykml import parser

def parse_madrid_metro():
    files = ['data/metro/Metro.kml', 'data/metro/MetroLigero.kml']
    places = []
    for f in files:
        with open(f, 'rb') as x:
            xml = etree.parse(x)
        k = parser.fromstring(etree.tostring(xml))
        places.extend(k.findall('.//{http://www.opengis.net/kml/2.2}Placemark'))

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

def parse_bcn_metro():
    files = ['data/metro/TMB_EST.kml', 'data/metro/TRAM_EST.kml']
    places = []
    for f in files:
        with open(f, 'rb') as x:
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

def parse_bilbao_metro():
    with open('data/metro/stops.txt') as f:
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
            loc['coordinates'] = [ float(row[4]), float(row[3]) ]
            station['loc'] = loc

            stations.append(station)

    return stations

def parse_metro():
    station_parsers = [
        ['Madrid', parse_madrid_metro],
        ['Barcelona', parse_bcn_metro],
        ['Bilbao', parse_bilbao_metro],
    ]
    client = pymongo.MongoClient()
    db = client.openmotion
    metro = db.metro

    for parser in station_parsers:
        stations = parser[1]()
        count = 0
        for s in stations:
            res = metro.update({'loc' : s['loc']}, s, upsert=True)

            if res['updatedExisting'] == False:
                count = count + 1
        print(parser[0], "inserted", count, "new records.")

    client.disconnect()

def drop_and_recreate():
    client = pymongo.MongoClient()
    db = client.openmotion
    db.drop_collection('metro')
    client.disconnect()

    client = pymongo.MongoClient()
    db = client.openmotion
    db.metro.ensure_index([('loc', pymongo.GEOSPHERE)])
    client.disconnect()

if __name__ == "__main__":
    drop_and_recreate()
    parse_metro()

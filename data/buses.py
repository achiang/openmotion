#!/usr/bin/env python3

import bng
import csv
import simplejson as json
import pymongo
from lxml import etree
from pykml import parser

def parse_madrid_bus(basepath):
    files = ['EMT.kml', 'Interurbanos.kml']
    places = []
    for f in files:
        with open(basepath + f, 'rb') as x:
            xml = etree.parse(x)
        k = parser.fromstring(etree.tostring(xml))
        places.extend(k.findall('.//{http://www.opengis.net/kml/2.2}Placemark'))

    stations = []
    count = 0
    for p in places:
        station = { 'mode': 'bus' }
        station['city'] = 'Madrid'
        station['name'] = p.name.text

        coords = [float(c.strip()) for c in p.Point.coordinates.text.split(',')]

        loc = {}
        loc['type'] = 'Point'
        loc['coordinates'] = coords
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_bcn_bus(basepath):
    with open(basepath + 'BUS_EST.kml', 'rb') as f:
        xml = etree.parse(f)

    k = parser.fromstring(etree.tostring(xml))
    places = k.findall('.//{http://www.opengis.net/kml/2.2}Placemark')

    stations = []
    count = 0
    for p in places:
        station = { 'mode': 'bus' }
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

def parse_valencia_bus(basepath):
    with open(basepath + 'Emt_paradas.KML', 'rb') as f:
        xml = etree.parse(f)

    k = parser.fromstring(etree.tostring(xml))
    places = k.findall('.//{http://www.opengis.net/kml/2.2}Placemark')

    stations = []
    count = 0
    for p in places:
        station = { 'mode': 'bus' }
        station['city'] = 'Valencia'

        data = p.findall('.//{http://www.opengis.net/kml/2.2}Data')
        for d in data:
            if d.attrib['name'] == 'numportal':
                station['name'] = str(d.value)

        coords = [float(c.strip()) for c in p.Point.coordinates.text.split(',')]

        loc = {}
        loc['type'] = 'Point'
        loc['coordinates'] = coords
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_bilbao_bus(basepath):
    with open(basepath + 'stops.txt') as f:
        reader = csv.reader(f, delimiter=',')

        stations = []
        for row in reader:
            if row[0] == "stop_id":
                continue

            station = { 'mode': 'bus' }
            station['city'] = 'Bilbao'
            station['name'] = row[2]            # stop_name

            loc = {}
            loc['type'] = 'Point'
            loc['coordinates'] = [ float(row[5]), float(row[4]) ]
            station['loc'] = loc

            stations.append(station)

    return stations

def parse_malaga_bus(basepath):
    # If Malaga gets more than 1 bus stop, we'll do some parsing then ;)
    station = { 'mode': 'bus' }
    station['city'] = 'Malaga'
    station['name'] = 'Paseo de los Tilos'

    loc = {}
    loc['type'] = 'Point'
    loc['coordinates'] = [-4.4342172937, 36.7130306843]
    station['loc'] = loc

    return [station]

def parse_london_bus(basepath):
    with open(basepath + 'bus-stops.csv') as f:
        reader = csv.reader(f, delimiter=',')

        stations = []
        for row in reader:
            if row[0] == "Stop_Code_LBSL":
                continue

            station = { 'mode': 'bus' }
            station['city'] = 'London'
            station['name'] = row[3]            # Stop_Name

            loc = {}
            loc['type'] = 'Point'
            lng, lat = bng.tolnglat(int(row[4]), int(row[5]))
            loc['coordinates'] = [ lng, lat ]
            station['loc'] = loc

            stations.append(station)

    return stations

def parse_uk_bus(basepath):
    json_data = open(basepath + 'UK.json').read()
    data = json.loads(json_data)

    stations = []
    for d in data:
        stations.append(d)

    return stations

def do_import(mongo_uri, basepath):
    station_parsers = [
        ['Madrid', parse_madrid_bus],
        ['Barcelona', parse_bcn_bus],
        ['Valencia', parse_valencia_bus],
        ['Malaga', parse_malaga_bus],
        ['Bilbao', parse_bilbao_bus],
        ['London', parse_london_bus],
        ['UK', parse_uk_bus],
    ]
    client = pymongo.MongoClient(mongo_uri)
    db = client.openmotion
    buses = db.buses

    for parser in station_parsers:
        buses.insert(parser[1](basepath))

    client.disconnect()

if __name__ == "__main__":
    from lib import get_mongo_config, get_basepath, mongo_drop, mongo_index
    mode = 'buses'
    mongo_uri = get_mongo_config()
    basepath = get_basepath() + mode + '/'

    mongo_drop(mongo_uri, mode)
    do_import(mongo_uri, basepath)
    mongo_index(mongo_uri, mode)

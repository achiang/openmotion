#!/usr/bin/env python3

import csv
import pymongo
import simplejson as json
from lxml import etree

def parse_london_bikes():
    tree = etree.parse('data/bikes/livecyclehireupdates.xml')
    root = tree.getroot()

    stations = []
    for s in root:
        station = {}
        station['city'] = 'London'
        lat = ""
        lng = ""

        for attr in s:
            if attr.tag == "name":
                station['name'] = attr.text
            if attr.tag == "terminalName":
                station['station_id'] = attr.text
            if attr.tag == "lat":
                lat = attr.text
            if attr.tag == "long":
                lng = attr.text

        loc = {}
        loc['type'] = 'Point'
        loc['coordinates'] = [ float(lng), float(lat) ]
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_bcn_bikes():
    tree = etree.parse('data/bikes/bcnbicing.xml')
    root = tree.getroot()

    stations = []
    for s in root:
        station = {}
        station['city'] = 'Barcelona'
        lat = ""
        lng = ""
        street = ""
        streetNumber = ""

        if s.tag == "updatetime":
            continue

        for attr in s:
            if attr.tag == "street":
                street = attr.text
            if attr.tag == "streetNumber":
                streetNumber = attr.text
            if attr.tag == "id":
                station['station_id'] = attr.text
            if attr.tag == "lat":
                lat = attr.text
            if attr.tag == "long":
                lng = attr.text

        loc = {}
        loc['type'] = 'Point'
        loc['coordinates'] = [ float(lng), float(lat) ]
        station['loc'] = loc

        station['name'] = " ".join(it for it in [streetNumber, street] if it)

        stations.append(station)

    return stations

def parse_valencia_bikes():
    json_data = open('data/bikes/Valenbisi.JSON').read()
    data = json.loads(json_data)

    stations = []
    for f in data['features']:
        station = {}
        station['city'] = 'Valencia'
        station['station_id'] = f['properties']['name']

        number = f['properties']['number']
        address = f['properties']['address']
        station['name'] = " ".join(it for it in [number, address] if it)
        station['loc'] = f['geometry']

        stations.append(station)

    return stations

def parse_zaragoza_bikes():
    json_data = open('data/bikes/zaragoza.json').read()
    data = json.loads(json_data)

    stations = []
    for d in data['response']['docs']:
        station = {}
        station['city'] = 'Zaragoza'
        station['station_id'] = d['id']
        station['name'] = d['title']

        loc = {}
        loc['type'] = 'Point'
        loc['coordinates'] = [float(x) for x in d['coordenadas_p'].split(',')]
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_malaga_bikes():
    stations = []
    with open('data/bikes/Estacionamientos.csv') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == "ID":
                continue

            station = {}
            station['city'] = 'Malaga'
            station['station_id'] = row[11]     # ID_EXTERNO
            station['name'] = row[3]            # DIRECCION

            loc = {}
            loc['type'] = 'Point'
            loc['coordinates'] = [ float(row[10]), float(row[9]) ]
            station['loc'] = loc

            stations.append(station)

    return stations

def parse_bikes():
    station_parsers = [
        ['London', parse_london_bikes],
        ['Barcelona', parse_bcn_bikes],
        ['Valencia', parse_valencia_bikes],
        ['Malaga', parse_malaga_bikes],
        ['Zaragoza', parse_zaragoza_bikes],
    ]

    client = pymongo.MongoClient()
    db = client.openmotion
    bikes = db.bikes

    for parser in station_parsers:
        stations = parser[1]()
        count = 0
        for s in stations:
            res = bikes.update({'city': s['city'],
                                'station_id' : s['station_id']},
                                s, upsert=True)

            if res['updatedExisting'] == False:
                count = count + 1
        print(parser[0], "inserted", count, "new records.")

    client.disconnect()

def drop_and_recreate():
    client = pymongo.MongoClient()
    db = client.openmotion
    db.drop_collection('bikes')
    client.disconnect()

    client = pymongo.MongoClient()
    db = client.openmotion
    db.bikes.ensure_index([('loc', pymongo.GEOSPHERE)])
    db.bikes.ensure_index([('city', pymongo.ASCENDING),
                           ('station_id', pymongo.ASCENDING)], unique=True)
    client.disconnect()

if __name__ == "__main__":
    drop_and_recreate()
    parse_bikes()

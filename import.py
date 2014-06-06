#!/usr/bin/env python3

import csv
import pymongo
import simplejson as json
from lxml import etree

def parse_london_bikes():
    tree = etree.parse('data/bikes/livecyclehireupdates.xml')
    root = tree.getroot()

    client = pymongo.MongoClient()
    db = client.openmotion
    bikes = db.bikes

    count = 0

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

        exists = bikes.find_one({'station_id' : station['station_id']})
        if exists:
            continue

        loc = {}
        loc['type'] = 'Point'
        loc['coordinates'] = [ float(lng), float(lat) ]
        station['loc'] = loc

        bikes.insert(station)
        count = count + 1

    client.disconnect()
    print("London Bikes inserted", count, "new records")

def parse_bcn_bikes():
    tree = etree.parse('data/bikes/bcnbicing.xml')
    root = tree.getroot()

    client = pymongo.MongoClient()
    db = client.openmotion
    bikes = db.bikes

    count = 0

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

        exists = bikes.find_one({'city': station['city'],
                                 'station_id' : station['station_id']})
        if exists:
            continue

        loc = {}
        loc['type'] = 'Point'
        loc['coordinates'] = [ float(lng), float(lat) ]
        station['loc'] = loc

        station['name'] = " ".join(it for it in [streetNumber, street] if it)

        bikes.insert(station)
        count = count + 1

    client.disconnect()
    print("BCN bikes inserted", count, "new records")

def parse_valencia_bikes():
    json_data = open('data/bikes/Valenbisi.JSON').read()
    data = json.loads(json_data)

    client = pymongo.MongoClient()
    db = client.openmotion
    bikes = db.bikes

    count = 0

    for f in data['features']:
        station = {}
        station['city'] = 'Valencia'
        station['station_id'] = f['properties']['name']

        number = f['properties']['number']
        address = f['properties']['address']
        station['name'] = " ".join(it for it in [number, address] if it)
        station['loc'] = f['geometry']

        exists = bikes.find_one({'city': station['city'],
                                 'station_id' : station['station_id']})
        if exists:
            continue

        bikes.insert(station)
        count = count + 1

    client.disconnect()
    print("Valencia bikes inserted", count, "new records")

def parse_zaragoza_bikes():
    json_data = open('data/bikes/zaragoza.json').read()
    data = json.loads(json_data)

    client = pymongo.MongoClient()
    db = client.openmotion
    bikes = db.bikes

    count = 0

    for d in data['response']['docs']:
        station = {}
        station['city'] = 'Zaragoza'
        station['station_id'] = d['id']
        station['name'] = d['title']

        loc = {}
        loc['type'] = 'Point'
        loc['coordinates'] = [float(x) for x in d['coordenadas_p'].split(',')]
        station['loc'] = loc

        exists = bikes.find_one({'city': station['city'],
                                 'station_id' : station['station_id']})
        if exists:
            continue

        bikes.insert(station)
        count = count + 1

    client.disconnect()
    print("Zaragoza bikes inserted", count, "new records")

def parse_malaga_bikes():

    client = pymongo.MongoClient()
    db = client.openmotion
    bikes = db.bikes

    count = 0

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

            exists = bikes.find_one({'city': station['city'],
                                     'station_id' : station['station_id']})
            if exists:
                continue

            bikes.insert(station)
            count = count + 1

    client.disconnect()
    print("Malaga bikes inserted", count, "new records")


if __name__ == "__main__":
    parse_london_bikes()
    parse_bcn_bikes()
    parse_valencia_bikes()
    parse_malaga_bikes()
    parse_zaragoza_bikes()

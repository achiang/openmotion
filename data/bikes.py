#!/usr/bin/env python3

import csv
import os
import pymongo
import simplejson as json
from lxml import etree

def parse_london_bikes(basepath):
    tree = etree.parse(basepath + 'livecyclehireupdates.xml')
    root = tree.getroot()

    stations = []
    for s in root:
        station = { 'mode' : 'bike' }
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

        loc = { 'type' : 'Point' }
        loc['coordinates'] = [ float(lng), float(lat) ]
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_bcn_bikes(basepath):
    tree = etree.parse(basepath + 'bcnbicing.xml')
    root = tree.getroot()

    stations = []
    for s in root:
        station = { 'mode' : 'bike' }
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

        loc = { 'type' : 'Point' }
        loc['coordinates'] = [ float(lng), float(lat) ]
        station['loc'] = loc

        station['name'] = " ".join(it for it in [streetNumber, street] if it)

        stations.append(station)

    return stations

def parse_valencia_bikes(basepath):
    json_data = open(basepath + 'Valenbisi.JSON').read()
    data = json.loads(json_data)

    stations = []
    for f in data['features']:
        station = { 'mode' : 'bike' }
        station['city'] = 'Valencia'
        station['station_id'] = f['properties']['name']

        number = f['properties']['number']
        address = f['properties']['address']
        station['name'] = " ".join(it for it in [number, address] if it)
        station['loc'] = f['geometry']

        stations.append(station)

    return stations

def parse_zaragoza_bikes(basepath):
    json_data = open(basepath + 'zaragoza.json').read()
    data = json.loads(json_data)

    stations = []
    for d in data['response']['docs']:
        station = { 'mode' : 'bike' }
        station['city'] = 'Zaragoza'
        station['station_id'] = d['id']
        station['name'] = d['title']

        loc = { 'type' : 'Point' }
        loc['coordinates'] = [float(x) for x in d['coordenadas_p'].split(',')]
        station['loc'] = loc

        stations.append(station)

    return stations

def parse_malaga_bikes(basepath):
    stations = []
    with open(basepath + 'Estacionamientos.csv') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == "ID":
                continue

            station = { 'mode' : 'bike' }
            station['city'] = 'Malaga'
            station['station_id'] = row[11]     # ID_EXTERNO
            station['name'] = row[3]            # DIRECCION

            loc = { 'type' : 'Point' }
            loc['coordinates'] = [ float(row[10]), float(row[9]) ]
            station['loc'] = loc

            stations.append(station)

    return stations

def do_import(mongo_uri, basepath):
    station_parsers = [
        ['London', parse_london_bikes],
        ['Barcelona', parse_bcn_bikes],
        ['Valencia', parse_valencia_bikes],
        ['Malaga', parse_malaga_bikes],
        ['Zaragoza', parse_zaragoza_bikes],
    ]

    client = pymongo.MongoClient(mongo_uri)
    db = client.openmotion
    bikes = db.bikes

    for parser in station_parsers:
        bikes.insert(parser[1](basepath))

    client.disconnect()

if __name__ == "__main__":
    from lib import get_mongo_config, get_basepath, mongo_drop, mongo_index
    mode = 'bikes'
    mongo_uri = get_mongo_config()
    basepath = get_basepath() + mode + '/'

    mongo_drop(mongo_uri, mode)
    do_import(mongo_uri, basepath)
    mongo_index(mongo_uri, mode)

import os
import pymongo
import re

def pluralize(noun):
    # (pattern, search, replace) regex english plural rules tuple
    rule_tuple = (
        ('[ml]ouse$', '([ml])ouse$', '\\1ice'),
        ('child$', 'child$', 'children'),
        ('booth$', 'booth$', 'booths'),
        ('foot$', 'foot$', 'feet'),
        ('ooth$', 'ooth$', 'eeth'),
        ('l[eo]af$', 'l([eo])af$', 'l\\1aves'),
        ('sis$', 'sis$', 'ses'),
        ('man$', 'man$', 'men'),
        ('ife$', 'ife$', 'ives'),
        ('eau$', 'eau$', 'eaux'),
        ('lf$', 'lf$', 'lves'),
        ('[sxz]$', '$', 'es'),
        ('[^aeioudgkprt]h$', '$', 'es'),
        ('(qu|[^aeiou])y$', 'y$', 'ies'),
        ('$', '$', 's')
        )
    def regex_rules(rules=rule_tuple):
        for line in rules:
            pattern, search, replace = line
            yield lambda word: re.search(pattern, word) and re.sub(search, replace, word)

    for rule in regex_rules():
        result = rule(noun)
        if result:
            return result

def get_basepath():
    return os.path.dirname(os.path.realpath(__file__)) + '/'

def get_mongo_config():
    with open(get_basepath() + '../config/config.js') as f:
        for line in f:
            if 'mongo_host' in line:
                mongo_host = line.split(':')[-1].strip().replace("\"", "")
            if 'mongo_port' in line:
                mongo_port = line.split(':')[-1].strip()

    return 'mongodb://' + mongo_host + ':' + mongo_port + '/'

def drop_and_recreate(mongo_uri, collection):
    client = pymongo.MongoClient(mongo_uri)
    db = client.openmotion
    db.drop_collection(collection)
    client.disconnect()

    client = pymongo.MongoClient(mongo_uri)
    db = client.openmotion
    db.collection.ensure_index([('loc', pymongo.GEOSPHERE)])
    client.disconnect()


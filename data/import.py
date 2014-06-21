#!/usr/bin/env python3

from lib import get_mongo_config, get_basepath, drop_and_recreate

if __name__ == "__main__":
    mongo_uri = get_mongo_config()
    basepath = get_basepath()

    transports = ['bikes', 'metros', 'trains', 'buses']
    for t in transports:
        drop_and_recreate(mongo_uri, t)

    modules = map(__import__, transports)
    for m in modules:
        m.do_import(mongo_uri, basepath)

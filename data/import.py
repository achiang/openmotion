#!/usr/bin/env python3

from lib import get_mongo_config, get_basepath

import import_bike

if __name__ == "__main__":
    mongo_uri = get_mongo_config()
    basepath = get_basepath()

    import_bike.drop_and_recreate(mongo_uri)

    import_bike.parse_bikes(mongo_uri, basepath)

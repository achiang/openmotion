import os

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


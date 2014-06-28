OpenMotion -- REST endpoints for opengov data
=============================================

Small demo server to provide geospatial municipal infrastructure searches
for things like subway stops, city bike shares, bus stops, etc.

Built with:

    - nodejs
    - mongodb
    - python (to import data)
        - pip3 install pykml

Deploying
=========

This app uses juju to help simplify deployment. To use it:

    juju bootstrap
    juju deploy --repository=./charms local:trusty/node-app openmotion
    juju deploy --config charms/precise/mongodb/mongodb.yaml cs:precise/mongodb
    juju add-relation mongodb openmotion

Note that the add-relation step may take a long time to import all the data.

Testing
=======

After it has been deployed, you can test with curl:

    curl -i "http://localhost:3000/v1/bikes?lat=51.52916347&lng=-0.109"

    [{"dis":0.000010538015170703655,"obj":{"station_id":"001023","loc":{"coordinates":[-0.109970527,51.52916347],"type":"Point"},"city":"London","name":"River Street , Clerkenwell","_id":"53a1c425bacb0f8e5efa2df8"}}]

    curl -i "http://localhost:3000/v1/buses?lng=-2.909&lat=43.24895"

    [{"dis":0.0000047035625998511204,"obj":{"city":"Bilbao","loc":{"type":"Point","coordinates":[-2.90937,43.24895]},"name":"Cocherito De Bilbao 14","_id":"53a4df790e6b8a5afd2b0728"}}]

    curl -i "http://localhost:3000/v1/trains?lat=41.866&lng=0.832"

    [{"dis":0.000012533992661555583,"obj":{"city":"Barcelona","loc":{"type":"Point","coordinates":[0.832769068267674,41.8664332634197]},"name":"Sant Llorenç de Montgai","_id":"53a4df440e6b8a5afd2ada3c"}}]

    curl -i "http://localhost:3000/v1/metros?lat=41.4304&lng=2.222"

    [{"dis":0.000011878864177520727,"obj":{"city":"Barcelona","loc":{"type":"Point","coordinates":[2.22290444983689,41.4304584678793]},"name":"Encants de Sant Adrià","_id":"53a4df430e6b8a5afd2ad819"}}]

misc notes
==========

http://docs.mongodb.org/manual/tutorial/build-a-2dsphere-index/

> db.runCommand({geoNear: "bikes", near: { type: "Point", coordinates: [ -0.109, 51.52916347] }, spherical: true, maxDistance: 100 })

For bcn biking, need to replace all escaped html with utf-8 equivs. I did
this manually in vim (ugh).

For London bus-stops, had to:

  - vi bus-stops.csv
    :set nobomb
    :wq

git subtree add --prefix=charm --squash git@github.com:charms/node-app.git master

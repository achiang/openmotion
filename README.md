OpenMotion -- REST endpoints for opengov data
=============================================

Small demo server to provide geospatial municipal infrastructure searches
for things like subway stops, city bike shares, bus stops, etc.

Built with:

    - nodejs
    - mongodb
    - python (to import data)
        - pip3 install pykml


misc notes
==========

http://docs.mongodb.org/manual/tutorial/build-a-2dsphere-index/

> db.runCommand({geoNear: "bikes", near: { type: "Point", coordinates: [ -0.109, 51.52916347] }, spherical: true, maxDistance: 100 })

curl -i http://127.0.0.1:3000/bike/51.52916347/-0.109
[{"dis":0.000010538015170703655,"obj":{"station_id":"001023","loc":{"coordinates":[-0.109970527,51.52916347],"type":"Point"},"city":"London","name":"River Street , Clerkenwell","_id":"53a1c425bacb0f8e5efa2df8"}}]

For bcn biking, need to replace all escaped html with utf-8 equivs. I did
this manually in vim (ugh).

For London bus-stops, had to:

  - vi bus-stops.csv
    :set nobomb
    :wq

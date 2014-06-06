OpenMotion -- REST endpoints for opengov data
=============================================

Small demo server to provide geospatial municipal infrastructure searches
for things like subway stops, city bike shares, bus stops, etc.

Built with:

    - nodejs
    - mongodb
    - python (to import data)


misc notes
==========

http://docs.mongodb.org/manual/tutorial/build-a-2dsphere-index/

> db.runCommand({geoNear: "bikes", near: { type: "Point", coordinates: [ -0.109, 51.52916347] }, spherical: true, maxDistance: 100 })

For bcn biking, need to replace all escaped html with utf-8 equivs. I did
this manually in vim (ugh).

Bikes = new Meteor.Collection("bikes");

if (Meteor.isClient) {
    var map;
    Meteor.subscribe('bikes');

    Template.hello.greeting = function () {
        return "OpenMotion";
    };

    Template.hello.events({
        'click input': function () {
          // template data, if any, is available in 'this'
          if (typeof console !== 'undefined')
            console.log("You pressed the button");
        }
    });

    Template.map.created = function () {
        Bikes.find({}).observe({
            added: function(bike) {
                var latlng = L.latLng(bike.loc.coordinates[1], bike.loc.coordinates[0]);
                var marker = new L.Marker(latlng)
                                .bindPopup(bike.name)
                                .on('mouseover', function(e) {
                                    this.openPopup();
                                })
                                .on('mouseout', function(e) {
                                    this.closePopup();
                                });
                map.addLayer(marker);
            }
        });
    };

    var map_search = function () {
        var bounds = map.getBounds();
        var bbox = [[bounds._southWest.lng, bounds._southWest.lat],
                    [bounds._northEast.lng, bounds._northEast.lat]];
        var bikes = Bikes.find( { loc : { $geoWithin : { $box : bbox }}});
        console.log(bikes);
    }

    Template.map.rendered = function () {
        L.Icon.Default.imagePath = 'packages/leaflet/images';

        if (!map) {
            map = L.map('map_canvas').setView([51.5073, -0.1277], 13);
            L.tileLayer('http://{s}.tiles.mapbox.com/v3/chizang.ibio2bdk/{z}/{x}/{y}.png', {
                attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
                maxZoom: 18
            }).addTo(map);

            map.on('dragend', map_search)
               .on('zoomend', map_search);
        }
    };


}

if (Meteor.isServer) {
    Meteor.startup(function () {
    });

    Meteor.publish('bikes', function() {
        return Bikes.find({'city': 'London'});
    });
}

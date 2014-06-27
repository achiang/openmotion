var config = require('./config/config');
var restify = require('restify');
var mongoose = require('mongoose');
var server = restify.createServer({name: config.name});

var mongo_uri = 'mongodb://' + config.mongo_host + ':' + config.mongo_port;
mongo_uri += '/' + config.name;
mongoose.connect(mongo_uri);

var Schema = mongoose.Schema;
var BikeSchema = new Schema({
    name: String,
    station_id: String,
    loc: { type: {}, index: '2dsphere' },
    city: String
});

server
    .use(restify.fullResponse())
    .use(restify.queryParser())
    .use(restify.bodyParser());

server.listen(config.listen_port, function() {
    console.log('%s listening at %s', server.name, server.url);
});

server.get('/:ver/:mode', function(req, res, next) {
    next(req.params.ver + req.params.mode);
});

mongoose.model('Bike', BikeSchema);
var Bike = mongoose.model('Bike');

server.get({
    name: 'v1bikes',
    path: '/:ver/:mode'
}, function(req, res, next) {
    var lat = parseFloat(req.query.lat);
    var lng = parseFloat(req.query.lng);

    if (isNaN(lat) || isNaN(lng)) {
        res.send(400, "Bad or missing lat or lng parameter");
        next();
    }

    var point = {type: 'Point', coordinates: [lng, lat]};

    // http://stackoverflow.com/q/22623998/
    Bike.geoNear(point, { maxDistance: 100/6378137, spherical: true }
        , function (err, data) {
            if (err)
                return next(new restify.InvalidArgumentError(err.errmsg));
                
            res.send(200, data);
            next();
        });
});


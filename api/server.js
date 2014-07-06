var config = require('./config/config');
var models = require('./models');
var restify = require('restify');
var async = require('async');
var inflection = require('inflection');
var server = restify.createServer({name: config.name});

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

server
    .use(restify.fullResponse())
    .use(restify.queryParser())
    .use(restify.bodyParser());

server.listen(config.listen_port, function() {
    console.log('%s listening at %s', server.name, server.url);
});

server.get(/v1\/(all|bikes|buses|trains|metros)/, function(req, res, next) {
    var lat = parseFloat(req.query.lat);
    var lng = parseFloat(req.query.lng);
    var point = {type: 'Point', coordinates: [lng, lat]};

    if (isNaN(lat) || isNaN(lng)) {
        res.send(400, "Bad or missing lat or lng parameter");
        next();
    }

    var ret = []
    if (req.params[0] === "all")
        var collections = [ models.Bike, models.Train, models.Metro, models.Bus ];
    else
        var collections = [ models[inflection.singularize(req.params[0]).capitalize()] ];

    async.each(collections
        ,function eachCollection(collection, eachCallback) {
            // http://stackoverflow.com/q/22623998/
            collection.geoNear(point, { maxDistance: 100/6378137, spherical: true }
            ,function(err, data) {
                if (err)
                    return eachCallback(err);

                ret = ret.concat(data);
                eachCallback(null);
            });
        }
    ,function eachFinally(error) {
        if (error)
            return next(new restify.InvalidArgumentError(err.errmsg));

        res.send(200, ret);
        next();
    });
});


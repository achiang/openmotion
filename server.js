var config = require('./config/config');
var models = require('./models');
var restify = require('restify');
var server = restify.createServer({name: config.name});

server
    .use(restify.fullResponse())
    .use(restify.queryParser())
    .use(restify.bodyParser());

server.listen(config.listen_port, function() {
    console.log('%s listening at %s', server.name, server.url);
});

server.get(/v1\/(bikes|buses|trains|metros)/, function(req, res, next) {
    var lat = parseFloat(req.query.lat);
    var lng = parseFloat(req.query.lng);
    var point = {type: 'Point', coordinates: [lng, lat]};

    if (isNaN(lat) || isNaN(lng)) {
        res.send(400, "Bad or missing lat or lng parameter");
        next();
    }

    switch (req.params[0]) {
        case "bikes":
            var model = models.Bike;
            break;
        case "buses":
            var model = models.Bus;
            break;
        case "trains":
            var model = models.Train;
            break;
        case "metros":
            var model = models.Metro;
            break;
    }

    // http://stackoverflow.com/q/22623998/
    model.geoNear(point, { maxDistance: 100/6378137, spherical: true }
        , function (err, data) {
            if (err)
                return next(new restify.InvalidArgumentError(err.errmsg));
                
            res.send(200, data);
            next();
        });
});


var mongoose = require('mongoose');

var mongo_uri = 'mongodb://' + config.mongo_host + ':' + config.mongo_port;
mongo_uri += '/' + config.name;
mongoose.connect(mongo_uri);

var Schema = mongoose.Schema;
var BikeSchema = new Schema({
    name: String,
    mode: String,
    station_id: String,
    loc: { type: {}, index: '2dsphere' },
    city: String
});
var Bike = mongoose.model('Bike', BikeSchema);

var BusSchema = new Schema({
    name: String,
    mode: String,
    station_id: String,
    loc: { type: {}, index: '2dsphere' },
    city: String
});
var Bus = mongoose.model('Bus', BusSchema);

var TrainSchema = new Schema({
    name: String,
    mode: String,
    station_id: String,
    loc: { type: {}, index: '2dsphere' },
    city: String
});
var Train = mongoose.model('Train', TrainSchema);

var MetroSchema = new Schema({
    name: String,
    mode: String,
    station_id: String,
    loc: { type: {}, index: '2dsphere' },
    city: String
});
var Metro = mongoose.model('Metro', MetroSchema);

module.exports = {
    Bike: Bike,
    Bus: Bus,
    Train: Train,
    Metro: Metro
};

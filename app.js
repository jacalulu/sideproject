
/**
 * Module dependencies.
 */

var express = require('express');
var routes = require('./routes');
var user = require('./routes/user');
var http = require('http');
var path = require('path');
var nib = require('nib');
var stylus = require('stylus');
var fs = require('fs');
var hbs = require('hbs');

var getRoutes = require('./routes/index.js');

var AJAXs = require('ajaxs');
var api = new AJAXs();

var app = express();

// all environments
app.set('port', process.env.PORT || 3000);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');
app.use(express.favicon());
app.use(express.logger('dev'));
app.use(express.json());
app.use(express.urlencoded());
app.use(express.methodOverride());
app.use(app.router);
app.use(stylus.middleware({
	src: path.join(__dirname, 'public'),
	compile: function (str, path){ return stylus(str).set("filename", path).set("compress", true).use(nib()); }
}));
app.use(express.static(path.join(__dirname, 'public')));
app.use(api.middleware());


// development only
if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}

app.get('/', getRoutes.home);
app.get('/jaclynkonzelmann', function(req, res){
	res.render('index.hbs');
})


http.createServer(app).listen(app.get('port'), function(){
  console.log('Express server listening on port ' + app.get('port'));
});

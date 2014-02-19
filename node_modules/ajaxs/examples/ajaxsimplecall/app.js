var express = require('express');
var app = express();
var AJAXs = require('ajaxs');

// this will default to the ajaxs directory
var myAjaxMiddleware = new AJAXs();
// log requests
app.use(express.logger('dev'));

app.use(express.static(__dirname + '/public'));
// use the ajax middleware
app.use(myAjaxMiddleware.middleware());

// this examples does not have any routes, however
// you may `app.use(app.router)` before or after these
// static() middleware. If placed before them your routes
// will be matched BEFORE file serving takes place. If placed
// after as shown here then file serving is performed BEFORE
// any routes are hit:
app.use(app.router);

app.listen(3000);
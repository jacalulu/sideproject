var fs 	    = require('fs');
var path    = require('path');
var url 	= require('url');
var util 	= require('util');

const DEFAULT_API_DIRECTORY = 'ajaxs';
const SCRIPT_LOCATION       = '../clientjs/client.js';
const DEFAULT_TIMEOUT 		= 30 * 1000;
const TEMPLATE_LOCATION     = path.resolve(__dirname,SCRIPT_LOCATION);

var cacheAPIs  = {};
console.log(TEMPLATE_LOCATION);
var RegularCacheClient = fs.readFileSync(TEMPLATE_LOCATION,'utf8');

function getAbsolutePath( file ) {
	return path.resolve( process.cwd(), file);
}

/**
 * Synchronously retrieve the fixed filename.
 * @param { string } filename The filename to remove the extension from
 */
function getExtensionlessFilename( filename ) {
	return filename.substr( 0, filename.length - path.extname( filename ).length);
}

/**
 * Synchronously create a template
 */
function templateWithArgs( apiDir, apiName, apiFuncName ) {
	cacheAPIs[apiName] = RegularCacheClient
			.replace('%%api.root%%',apiDir)
			.replace('%%api.name%%',apiName)
			.replace('%%api.funcs%%',JSON.stringify(apiFuncName));	
}

/**
 * Synchronously copy an arguments object array.
 * @internal 
 * @param { object } args the objects array
 */
function copyArgumentsArray(args) {
	var copy = [];
	var index = 0;
	for (var i in args) {
		copy[index] = args[i];
		index++;
	}
	return copy;
}

/*
 * Synchronously retrieve all the api files in a specific dir.
 *
 * @internal
 * @param { string } apiDir The relative api directory.
 * @returns { object } contains a map of apis
 */
function getAllApis( apiDir ) {
	var localApiDir    = apiDir,
		apis = {},
		apiDirPath = getAbsolutePath(apiDir);

	var	apiFiles = fs.readdirSync(apiDirPath);

	apiFiles.forEach( function( possibleFile ) {

		var alteredPath = path.resolve(apiDirPath,possibleFile);

		if( fs.statSync(alteredPath).isFile() ) {
			var api = require(getAbsolutePath("."+path.sep+localApiDir+path.sep+possibleFile));
			
			var funcs = Object.getOwnPropertyNames(api).filter(function isApiFunc(property){
				return typeof api[property] === 'function';
			});

			var funcObj = funcs.reduce( function reduceToMap( previous, current, index, array) {
				previous[current] = api[current];
				return previous;
			},{});

			// Strip out the extension
			var apiName = getExtensionlessFilename( possibleFile );
			
			templateWithArgs( apiDir, apiName, funcs );
			apis[apiName] = { funcs: funcObj, 
								  api: api };
		}
	});

	return apis;
}


/**
 * Asynchronous call to read the raw body from the request that we have deemed,
 * as an API request.
 *
 * NOTE: This function implements a workaround if the middleware is placed 
 * after the body parser in the connect stack.
 * 
 * @internal
 * @param { object } req an expressjs http request object.
 * @param { object } res an expressjs http response object.
 * @param { function } rawBodyCallback a callback function once the body has been read.
 * @param { object } callback scopt 
 */
function readRawBody(req,res,rawBodyCallback,callbackScope) {

	if ( typeof req._body !== 'undefined' && req._body ) { 
		rawBodyCallback.call(callbackScope,req,res);
	} else {
		req.rawBody = '';
	  	req.setEncoding('utf8');

	  	req.on('data', function(chunk) { 
	    	req.rawBody += chunk;
	  	});

	  	req.on('end', function() {
	    	rawBodyCallback.call(callbackScope,req,res);
	  	});
	}
	
}


/**
 * AJAXs Object is initialized wiht a directory, in which to pull files.
 * 
 * @param { string } apiDir The relative api directory. If unset will defauls to 'ajaxs'
 */
 function AJAXs(apiDir) {
	this.apiDir = apiDir || DEFAULT_API_DIRECTORY;
	this.ajaxApis = {};
}

AJAXs.prototype.intialize = function() {
	this.ajaxApis = getAllApis(this.apiDir);
}

AJAXs.prototype.middleware = function() {
	var scopedThis = this;
	scopedThis.intialize();
	return function( req,res,next ) {
		return scopedThis.requestHandler(req,res,next);
	}
}

AJAXs.prototype.requestHandler = function( req, res, next) {
	var requestComponents = req.url.split('/').filter(function( requestArray ) {
		return requestArray && requestArray.length;
	});

	// if we are fielding a request for elements that are pre-fixed with our request directory
	// then this will be the handler
	if ( requestComponents.length >= 2 && requestComponents[0] === this.apiDir ) {
		var apiObjectSpecifier = getExtensionlessFilename(requestComponents[1]);
		
		if ( apiObjectSpecifier in this.ajaxApis ) {
			req.apiObject = this.ajaxApis[apiObjectSpecifier];
		} 
		else {
			// This is not an API that we have preloaded so..
			// you must be making a bad request
			res.send( 404 );
			return;
		}

		
		if ( requestComponents.length === 2 ) { // We have been requested to get the api file
			res.writeHead(200, {"Content-Type": "text/javascript"});
			res.end(cacheAPIs[apiObjectSpecifier]);
		} 
		else if (requestComponents.length === 3 )  {
			if ( requestComponents[2] in req.apiObject.funcs ) {
				req.apiFunc = req.apiObject.funcs[ requestComponents[2] ];
				readRawBody(req,res,this.requestFullBodyRead,this);
			}
			else {
				res.send( 404 );
				return;
			}
		} 
		else {
			res.send(404);
			return;
		}

	}  
	else {
		next();
	}
}

AJAXs.prototype.requestFullBodyRead = function( req, res ) {
	var timeoutInterval = null;
	var timeoutHit 		= false;

	function replyClosureFunction( ) {
		// Swallow this request the header and the request headers have already been sent
		if ( timeoutHit ) {
			return;
		}
		
		timeoutHit = true;

		if ( timeoutInterval ) {
			clearTimeout( timeoutInterval );
		}

		var callbackObj = {};
		var argumentList = copyArgumentsArray(arguments);
		callbackObj.args = argumentList;

		res.writeHead(200, {"Content-Type": "application/json"});
		res.end(JSON.stringify(callbackObj));
	}

	function timeoutOccured( ) {
		console.error( "Timeout content while request: " + req.url );
		timeoutHit = true;
		res.send( 501 );
	}

	var parsedJSONBody = null;

	try {
		parsedJSONBody = req.rawBody ? JSON.parse(req.rawBody) : req.body ;
	} 
	catch ( jsonParseException ) {
		res.send(400);
		return;
	}

	if ( parsedJSONBody && util.isArray(parsedJSONBody.args) ) {
		var timeoutTimerTime = DEFAULT_TIMEOUT;
		var argsArray = [];
		
		if ( 'needRequest' in req.apiObject.api && req.apiObject.api.needRequest ) {
			argsArray.push(req);
		}

		if ( 'timeout' in req.apiObject.api && typeof req.apiObject.api === 'number' ) {
			timeoutTimerTime = req.apiObject['timeout'];
		}
		
		argsArray = argsArray.concat(parsedJSONBody.args);

		argsArray.push(replyClosureFunction);
		timeoutInterval = setTimeout(timeoutOccured,timeoutTimerTime);

		try {
			req.apiFunc.apply( req.apiObject.api, argsArray);

			if (!parsedJSONBody.hasCb)  {
				timeoutHit = true;
				clearTimeout(timeoutInterval);
				res.send(200);
			}
		} catch (e) {
			console.error(e);
			console.error(e.stack);
			clearTimeout(timeoutInterval);
			res.send(500)
		}
	}
	else {
		console.error( "Improperlly formatted json data!");
		res.send( 400 );
	}
}

exports = module.exports = AJAXs;
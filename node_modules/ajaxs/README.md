Express Simple Ajax
-------------------

This will simplify the ajax calls, and runs as middleware for express. 

The interface was modelled after zerver, with a compatible interface with a few extra parameters.

To install:

```sh
	npm install ajaxs
```

# Advantages

 I have found with working with zerver, that it leads you to develop API-first services. One of the main issues that I found is that zerver was too bloated with unessary functionality as it was attempting to be a full web service, where most of the time I just wanted to use the ajax call simplicafication methods. 

 So without further adieu, I present AJAXsimple. It is a lightweight piece of express middleware that simplifies the process of making ajax web calls to you express application.

# Overview

## Server Side
Check out the examples directory, but as recap:

On your server side you must import the library, and set up express to use the middleware functionality:

```javascript
	var AJAXs = require('ajaxs');
	var myAjaxMiddleware = new AJAXs();
	app.use( myAjaxMiddleware.middleware() );
```

By default all the api objects will be read from ajaxs ( if unspecified in the constructor ). This can be changed to any base folder by altering the folling line in the previous example: ( the api folder will be referred to as api from now on)

```javascript
	var myAjaxMiddleware = new AJAXs('api');
```

Create a your api functions: 

```javascript
	exports.logwithcallback = function( logstring, callback ) {
		console.log( "Client says: " + logstring );
		var result = [ { name: "asdf" } ]; // do some work... 
		callback( result );
	}
```

## Client Side

Next in your client html you simply include the script refered to by /api/{{yourapifile}}.js. Then you are good to call any functions on your client side without having to worry about the backend ajax calls.

```html
<html>
	<head>
		<title>Test</title>
	</head>
	<body>
	</body>
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
	<script src="/api/logger.js"></script>
	<script>
		logger.log("Message From client!");
	</script>
</html>
```

The client side depends on jquery so you must include html before you include the your api.

# Additions

## Need the request object?

If you define the static property `needRequest` as true on the API object then the request will be passed through as the first parameter. This is useful if you have a cookie parser middleware running before ajaxs. For example check ajaxsimplewithreq.

## Need more time ?

There is a default timeout of 30 seconds before the server will respond with a 500 error, if you set `timeout` as a Numeric property on the API object ( in milli-seconds )  then you will be granted more time. Please check ajaxsimplewithreq.
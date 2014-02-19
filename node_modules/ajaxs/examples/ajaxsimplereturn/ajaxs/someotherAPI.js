exports.someotherfunction = function( page, offset, callback ) {
	console.log( "mimic doing some db call with page.. ");

	callback(null, {results: [ { name: "list elem 1" },{ name: "list elem 2" } ] } );
}
(function ($,window){
	var API_ROOT  = "%%api.root%%";
	var API_NAME  = "%%api.name%%";
	var API_FUNCS = %%api.funcs%%;
	var API_TIMEOUT = 30 * 1000;
	function copyArgumentsArray(args) {
		var copy = [];
		for (var i = 0; i < args.length; i++ ) {
			copy[i] = args[i];
		}
		return copy;
	}
	function sendAjaxCall( apiMethod, data, callback ) {

		function successAjaxCallback( xhrData, textStatus ) {
			var args = xhrData.args;
			callback && callback.apply(window,args);
		}
		var requestUrl = '/'+[API_ROOT,API_NAME,apiMethod].join('/');
		var dataObj = {};

		dataObj.args  = data;
		dataObj.hasCb = callback !== null;

		$.ajax({
			url: requestUrl,
			data: JSON.stringify(dataObj),
			timeout: API_TIMEOUT,
			type: 'POST',
			contentType: 'application/json'
		}).done( successAjaxCallback );
	}

	function getCallbackFromArgs( argumentList ) {
		var callbackSuccess = null;

		if ( argumentList && argumentList.length >= 1 ) {
			var lastArg = argumentList[argumentList.length - 1];
			if ( typeof lastArg === "function" ) {
				callbackSuccess = argumentList[argumentList.length - 1];
				argumentList.splice(argumentList.length - 1,1);
			}
		}

		return {
			callback: callbackSuccess,
			args: argumentList
		};
	}

	function clientAPIRequest(i,apiMethod) {
		window[API_NAME][apiMethod] = function () {
			var argumentList = copyArgumentsArray(arguments);
			var mutatedArgs = getCallbackFromArgs(argumentList);
			sendAjaxCall( apiMethod, mutatedArgs.args, mutatedArgs.callback );
		};
	}

	function initializeAPI( ) {
		window[API_NAME] = {};
		$.each(API_FUNCS,clientAPIRequest);
	}

	initializeAPI();
})($,window)
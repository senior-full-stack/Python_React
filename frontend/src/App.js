import React, { Component } from 'react';
import DMApp from './DMApp';
import Login from './Login';
import Config from './Config';

//var APP = {};
//var baseHost = Config.baseHost;
var baseUrl = Config.baseUrl;
//var APIVersion = Config.APIVersion;


/* CONFIG STUFF UP HERE */

String.prototype.capitalizeFirstLetter = function() {
	    return this.charAt(0).toUpperCase() + this.slice(1);
}

//fix for IE11 which doesn't support endswith
if (typeof String.prototype.endsWith !== 'function') {
	String.prototype.endsWith = function(suffix) {
		return this.indexOf(suffix, this.length - suffix.length) !== -1;
	};
}

class App extends Component {
	render() {
		if(sessionStorage["token"] && sessionStorage["token"] !== "") 
		{
			return <DMApp history="true" root={baseUrl}/>;
		}
		return <Login />;
	}
}

export default App;

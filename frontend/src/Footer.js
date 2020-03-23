import React, { Component } from 'react';

import Config from './Config';

import 'materialize-css';

var config = new Config();

var $ = window.jQuery = require('jquery');

var Footer = React.createClass({
	componentDidMount: function() {
		var self = this;

		$("#tos-link").click(function() {
			$('#tos-modal').modal();
            $('#tos-modal').modal('open');
		});

		var url = "/xajax/eula.txt";
		$.ajax(
			{
				url: url,
				beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						navigate(config.baseUrl+"/logout");
					}
				},
			}).done(function(data){
				$("#eula-modal-text").html(data);
			});

		var url = "/xajax/tos.txt";
		$.ajax(
			{
				url: url,
				beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						navigate(config.baseUrl+"/logout");
					}
				},
			}).done(function(data){
				$("#tos-modal-text").html(data);
			});
	},
	render: function() {
		return (
			<div>
				<div id="tos-modal" className="modal">
					<div className="modal-content">
						<h5 id="tos-modal-title">Terms and Conditions</h5>
						<div id="tos-modal-text">All rights reserved, all wrongs reversed.</div>
					</div>
					<div className="modal-footer">
						<a href="#!" className=" modal-action modal-close waves-effect waves-green btn-flat">Close</a>
					</div>
				</div>

				<div id="eula-modal" className="modal">
					<div className="modal-content">
						<h5 id="eula-modal-title">End User License Agreement</h5>
						<div id="eula-modal-text">I hereby declare that I am a hamster.</div>
					</div>
					<div className="modal-footer">
						<a id="eula_agree" href="#!" className=" modal-action modal-close waves-effect waves-green btn-flat">I agree</a>
						<a id="eula_decline" href="#!" className=" modal-action modal-close waves-effect waves-green btn-flat">I decline</a>
					</div>
				</div>

				<footer className="page-footer">
					<div className="footer-copyright light-blue lighten-2">
						<div className="container">
							<a className="grey-text text-lighten-4" target="_blank" href="http://www.digitalhealths.com">© 2016 Digital Health Solutions</a>
							<a className="grey-text text-lighten-4 right" href="#!" id="tos-link">Terms and Conditions</a>
						</div>
					</div>
				</footer>
			</div>
		);
	},
});

export default Footer;


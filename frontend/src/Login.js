import React, { Component } from 'react';
import Config from './Config';

import Footer from './Footer';

var config = new Config();

import 'materialize-css';

import pa_logo from './img/pa_logo.png';
import dhs_logo from './img/dhs_logo.png';

var $ = window.jQuery = require('jquery');

class Login extends Component {
	otp_enabled = false;
	baseUrl = "";

	constructor(props) {
		super(props);
		this.state = {
			state: 'idle',
			form_hide: '',
			disabled: false
		};

		this.onSubmit = this.onSubmit.bind(this);
		this.onChange = this.onChange.bind(this);
	}

	onSubmit (event) {
		event.preventDefault();
		var self = this;
		var url = config.baseHost+ "/api/"+config.APIVersion+"/users/login";
		this.setState({
			state: 'fetching',
			form_hide: "hide",
			disabled: true
		});

		var fdata = { email: $("#email").val(), password: $("#password").val(), serial: "N/A",otp: this.otp_enabled ? $("#otp").val() : ""};

		$.ajax({
			url: url,
			method: "POST",
			//dataType: "json",
			contentType: "application/json",
			data: JSON.stringify(fdata),
		}).done(function(data) {
			//TODO
			alert('login');
			console.log(data);
			// save JWT token to sessionStorage and find its expiration, save that too.
			if(data.token)
			{
				sessionStorage["token"] = data.token;
			}
			window.location.href = config.baseUrl+"/dashboard";
		}).fail(function(){
				//alert("failed");
				self.setState( { error: true, form_hide: '', state: 'failed', disabled: false } );
			});
	}

	onChange(event) {
		this.setState({value: event.target.value});
	}

	componentDidMount() {
	}

	render() {
		var error;
		if (this.state.error) {
			var style = { color: "#ef5350" };
			error = <h4 className="center-align" style={style}>Login failed</h4>
		}
		var spinner;
		if (this.state.state === "fetching") {
			spinner = <div className="progress"><div className="indeterminate"></div></div>
		}
		else {
			spinner = null
		}

		var otpml = "";
		if(this.otp_enabled) {

			otpml = <div className="input-field col s12">
				<input disabled={this.state.disabled} id="otp" type="number" className="validate" />
				<label Htmlfor="otp">One Time Code</label>
			</div> ;
		}

		return (
			<div className="section no-pad-bot" id="login-banner">
				<div className="container">
					<div className="row center-align center">
						<div className="col s12 m6 l4 push-l2">
							<img id="login_logo_dhs" src={dhs_logo}></img>
						</div>
						<div className="col s12 m6 l4 push-l2">
							<img id="login_logo_pa" src={pa_logo}></img>
						</div>
					</div>
					<div className="row">
						<h2 className="center-align">Log in</h2>
						{ error }
						<form className="col s12" onSubmit={this.onSubmit}>
							<div className="row">
								<div className="input-field col s6 push-s3">
									<input disabled={this.state.disabled} id="email" type="email" className="validate" value={this.state.email} onChange={this.onChange}/>
									<label htmlFor="email">Email</label>
								</div>
							</div>
							<div className="row">
								<div className="input-field col s6 push-s3">
									<input disabled={this.state.disabled} id="password" type="password" className="validate" value={this.state.password}/>
									<label htmlFor="password">Password</label>
								</div>
								{otpml}
							</div>
							<div className="row center">
								{spinner}
								<button className={"btn waves-effect waves-light "+ this.state.form_hide} type="submit" name="action">Submit
									<i className="material-icons right">send</i>
								</button>
							</div>
						</form>
					</div>
				</div>
				<Footer />
			</div>
		);
	}
}

export default Login;

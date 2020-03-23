import React, { Component } from 'react';
import Config from './Config';

import {_, DashboardAlerts} from './Alerts';

var config = new Config();

var Dashboard = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
			devices_no: 'working...',
			patients_no: 'working...',
		};
	},

	onSubmit: function(event) {
		//event.preventDefault();

		//TODO: should have a single dashboard API call to get all this, to not need mutliple

		var self = this;
		var url = "/api/"+config.APIVersion+"/devices";
		$.ajax(
			{
				url: url,
				beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}).done(function(data){
				self.setState({
					devices_no: data.devices.length
				});
			});

		url = "/api/"+config.APIVersion+"/patients";
		$.ajax(
			{
				url: url,
				beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}).done(function(data){
				self.setState({
					patients_no: data.patients.length
				});
			});

	},

	componentDidMount: function() {
		this.onSubmit();
	},

	render: function() {
		return (
			<section>
				<div className="row">
					<h3>Dashboard</h3> 
					<h4>Hello, {this.props.current_user.name}</h4> 
				</div>
				<div className="row">

					<div className="col s6 m3">
						<DashboardAlerts />
					</div>
					
					<div className="col s6 m3">
						<div className="card dashboard-card" style={{'minHeight': 200 + 'px', height: 'auto'}}>
					<div className="card-content" style={{'minHeight': 164 + 'px', height: 'auto'}}>
								<span className="card-title">Devices</span>
								<p>Your organization has {this.state.devices_no} devices</p>
							</div>
							<div className="card-action">
								<a href={config.baseUrl+"/devices"}>View Devices</a>
							</div>
						</div>
					</div>

					<div className="col s6 m3">
						<div className="card dashboard-card" style={{'minHeight': 200 + 'px', height: 'auto'}}>
					<div className="card-content" style={{'minHeight': 164 + 'px', height: 'auto'}}>

								<span className="card-title">Patients</span>
								<p>Your organization has {this.state.patients_no} patients</p>
							</div>
							<div className="card-action">
								<a href={config.baseUrl+"/patients"}>View Patients</a>
								{/*
								<br />
								<a href={config.baseUrl+"/reports"}>View Patients' Reports</a>
								*/}
							</div>
						</div>
					</div>

				</div>   
			</section>
		);
	}
});

export default Dashboard;

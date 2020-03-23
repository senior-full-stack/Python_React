import React from 'react';

import Device from './Device';

import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');

var unassigned_patients = [];

var Devices = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
			devices: '',
			loading: <div className="progress">
				<div className="indeterminate"></div>
			</div>,
		};
	},

	onSubmit: function(event) {
		//event.preventDefault();
		var self = this;
		var url = "/api/"+config.APIVersion+"/devices";
		self.setState({
			state: 'looking up devices...',
			devices: self.state.devices
		});
		$.ajax(
			{
				url: url,
				method: 'GET',
				beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}
		)
			.done(function(data){
				self.setState({
					state: 'idle',
					devices: data.devices.map(function(device){
						return (<Device key={device.name} name={device.name} language={device.language} last_seen={device.last_seen} medical_record_number={device.medical_record_number} patient_name={device.patient_name + ' ' + (device.patient_last_name || "")} current_user={self.props.current_user} unassigned_patients={unassigned_patients}/>);
					}),
					loading: '',
				});

				$(".assign-link").click(function() {
					var el = $(this);
					var ds = el.attr("data-device_serial");
					var mrn = el.attr("data-medical_record_number");
					var url = "/api/"+config.APIVersion+"/patients/"+mrn+"/assign/"+ds;
					$.ajax(
						{
							url: url,
							method: 'PUT',
							beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
							statusCode: {
								401: function() {
									$.navigate(config.baseUrl+"/logout");
								}
							},
						}
					)
						.done(function(data){
							//redirect back to devices
							window.location.href = config.baseUrl+"/devices";
						});
				});

				$(".unassign-button").click(function() {
					var confirmed = confirm("Are you sure you want to unassign the patient from this device?");
					if(confirmed !== true)	{
						return;
					}
					var el = $(this);
					var ds = el.attr("data-device_serial");
					var mrn = el.attr("data-medical_record_number");
					var url = "/api/"+config.APIVersion+"/patients/"+mrn+"/unassign/";
					$.ajax(
						{
							url: url,
							method: 'PUT',
							beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
							statusCode: {
								401: function() {
									$.navigate(config.baseUrl+"/logout");
								}
							},
						}
					)
						.done(function(data){
							//redirect back to devices
							window.location.href = config.baseUrl+"/devices";
						});
				});

				$(".delete-click").click(function() {
					var confirmed = confirm("Are you sure you want to delete this device?");
					if(confirmed !== true)	{
						return;
					}
					var el = $(this);
					var ds = el.attr("data-device_serial");
					var url = "/api/"+config.APIVersion+"/devices/"+ds+"/";
					$.ajax(
						{
							url: url,
							method: 'DELETE',
							beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
							statusCode: {
								401: function() {
									$.navigate(config.baseUrl+"/logout");
								}
							},
						}
					)
						.done(function(data){
							//redirect back to devices
							window.location.href = config.baseUrl+"/devices";
						});
				});
			});
	},

	getUnassignedPatients: function(event) {
		//event.preventDefault();
		var self = this;
		var url = "/api/"+config.APIVersion+"/patients?unassigned=True";
		self.setState({
			state: 'looking up devices...',
			devices: self.state.devices
		});
		$.ajax(
			{
				url: url,
				method: 'GET',
				beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}
		)
			.done(function(data){
				//put to unassigned_patients
				//re-do the on-submit thing, or do it after this?
				unassigned_patients = data.patients;
				//console.log(unassigned_patients);
				self.onSubmit();
			});
	},

	componentDidMount: function() {
		this.getUnassignedPatients();
		//this.onSubmit();
	},

	componentWillUnmount: function() {
		$(".unassign-button").unbind("click");
		$(".assign-click").unbind("click");
		$(".delete-click").unbind("click");
	},

	render: function() {
		var section_style = {
			"marginTop": "65px",
		};

		var delete_device;
		if(this.props.current_user.role == "admin") {
			delete_device = <th data-field="delete">Delete</th>
		}
		return (
			<section style={section_style}>
				<table>
					<thead>
						<tr>
							<th data-field="name">Name</th>
							<th data-field="last_seen">Last Seen</th>
							<th data-field="assignment">Assignment</th>
							{delete_device}
						</tr>
					</thead>
					<tbody>
						{this.state.devices}
					</tbody>
				</table>
				{this.state.loading}
			</section>
		);
	}
});

export default Devices;

import React from 'react';
import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');

var moment = require('moment');

var PatientOutcome = React.createClass({
	getInitialState: function() {
		return {
			sensors_not_collected_reason: "",
			other_inactivation_reason: "",
		};

	},

	onSubmit: function(event) {
		event.preventDefault();
		if(this.state.device.length > 0) {
			var confirmed = window.confirm("Warning - The patient you are currently trying to inactivate currently has a tablet assigned to its record.  If you want to still inactivate this patient, click the Update button and the tablet will automatically be unassigned.");
			if(confirmed !== true)	{
				return;
			}
		}
		var self = this;
		var url = "/api/"+config.APIVersion+"/deactivate/"+this.props.medical_record_number;

		var octime = new Date(this.state.occurred_date+" "+this.state.occurred_hour+":"+this.state.occurred_minute);

		var collected = false;
		if(this.state.sensors_collected == "yes") {
			collected = true;
		}

		var json_out = {};
		json_out["medical_record_number"] = this.props.medical_record_number;
		json_out["occurred"] = octime.toISOString();
		json_out["reason"] = this.state.reason;
		json_out["reason_other"] = this.state.other_inactivation_reason;
		json_out["sensors_not_collected_reason"] = this.state.sensors_not_collected_reason;
		json_out["sensors_collected"] = collected;


		//console.log("submit "+JSON.stringify(json_out));
		$.ajax(
			{
				type: 'POST',
				contentType: 'application/json; charset=UTF-8',
				dataType: 'json',
				data: JSON.stringify(json_out),
				url: url,
				beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}
		).done(function(data){
			$.navigate(config.baseUrl+"/patients");
			Materialize.toast('Patient successfully inactivated', 4000, 'rounded');
		});
	},

	doInit: function(event) {
		if(this.props.medical_record_number  !== 'undefined') {
			//do ajax call to get all user stuffs
			var self = this;
			var url = "/api/"+config.APIVersion+"/outcomes/"+this.props.medical_record_number;
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
			).done(function(data){

				self.setState({
					existing: true,
					name: data.patient.name,
					last_name: data.patient.last_name,
					DOB: data.patient.DOB,
					unit_floor: data.patient.unit_floor,
					pressure_injuries: data.pressure_injuries,
					device: data.patient.device,
					activation_status: data.activation_status,
					body_locations: data.patient.body_locations.map(function(bl, index){
						var occurrence = "None";
						var stage = "N/A";
						var wound_outcome = "N/A";
						if(bl.existing_wound) {
							occurrence = "Pre-Existing";
							stage = bl.wound_stage;
							wound_outcome = bl.wound_outcome;
						}
						else if(bl.is_wound) {
							occurrence = "New";
							stage = bl.wound_stage;
							wound_outcome = bl.wound_outcome;
						}

						return <tr key={self.props.medical_record_number+"|"+bl.JSID}>
							<td>{bl.JSID.toLowerCase().replace("_"," ").capitalizeFirstLetter()}</td>
							<td>{occurrence}</td>
							<td>{stage}</td>
							<td>{wound_outcome}</td>
						</tr>
					}),
					activations: data.activations.map(function(act, index){
						var dtmp = moment(new Date(act.occurred));
						var ddate = dtmp.format('YYYY-MM-DD');
						var ttime = dtmp.format('HH:mm');
						var invactivation_reason = act.reason;
						if(act.reason_other && act.reason_other.length > 0 && act.reason == "Other") {
							invactivation_reason = act.reason+": "+JSON.stringify(act.reason_other);
						}
						return <tr key={self.props.medical_record_number+"|activation|"+index}>
							<td>{act.status}</td>
							<td>{ddate}</td>
							<td>{ttime}</td>
							<td>{invactivation_reason}</td>
						</tr>
					}),

				});
				$.setup_pickadate(self);
			});
		}
	},

	onChange: function(e, ee) {
		var x = $(e.target).attr('id');
		if($(e.target).is(':checkbox')) {
			this.state[x] = $(e.target).prop("checked");
		}
		else {
			this.state[x] = e.target.value;
		}
		this.setState(this.state);
		$('#patient-outcome-form select').material_select();
	},

	componentDidUpdate: function() {
		//needed for materialize to render the select forms
		$('#patient-outcome-form select').material_select();
		// for HTML5 "required" attribute
		$("#patient-outcome-form select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
	},

	componentWillUnmount: function() {
		$(document).off("refresh-outcome");
	},

	componentDidMount: function() {
		this.doInit();
		var self = this;
		//needed for materialize to render the select forms
		$('#patient-outcome-form select').material_select();
		$('#patient-outcome-form select').on('change', this.onChange);
		// for HTML5 "required" attribute
		$("#patient-outcome-form select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
		$("#patient-outcome-form").on('submit', this.onSubmit);

		//bind to refresh
		$(document).on("refresh-outcome", function(evt, name) {
			self.doInit();
		});
	},

	onChange: function(e, ee) {
		var x = $(e.target).attr('id');
		this.state[x] = e.target.value;
		this.setState(this.state);
		$('#patient-outcome-form select').material_select();
	},


	render: function() {

		var self = this;

		var submit_text = "Add patient";
		if(this.state.medical_record_number) {
			submit_text = "Update patient";
		}

		var ehidden = "";
		if(this.props.edit_hidden) {
			ehidden = "hide";
		}

		var cannot_submit = true;

		var other_reason_hidden = "";
		var reason_hidden = "";

		if(this.state.reason !== "Other") {
			other_reason_hidden = "hide";
		}
		else {
			other_reason_hidden = "";
		}

		if(this.state.sensors_collected !== "no") {
			reason_hidden = "hide";
		}
		else {
			reason_hidden = "";
		}

		if(this.state.sensors_collected == "yes"  && this.state.reason != "Other"){
			cannot_submit = false;
		}
		else if(this.state.sensors_collected == "yes" && this.state.other_inactivation_reason.length > 1 && this.state.reason == "Other") {
			cannot_submit = false;
		}
		else if(this.state.sensors_not_collected_reason.length > 1 && this.state.sensors_collected == "no" && this.state.reason !== "Other") {
			cannot_submit = false;
		}
		else if(this.state.sensors_not_collected_reason.length > 1 && this.state.sensors_collected == "no" && this.state.other_inactivation_reason.length > 1 && this.state.reason == "Other") {
			cannot_submit = false;
		}

		var hide_form = "hide";
		if(this.state.activation_status == "Activated" || this.state.activation_status == "Reactivated") {
			hide_form = "";
		}

		return (
			<section className="new-patient">

				<div className="row">
					<div className="col s12 m6">
						<h4>Patient Information</h4>
						<ul className="collection">
							<li className="collection-item"><span className="patient-info-name">Name/ID:</span> <span className="patient-info-value">{this.state.name + ' ' + this.state.last_name}</span></li>
							<li className="collection-item"><span className="patient-info-name">DOB:</span> <span className="patient-info-value">{this.state.DOB}</span></li>
							<li className="collection-item"><span className="patient-info-name">Unit/Floor:</span> <span className="patient-info-value">{this.state.unit_floor}</span></li>
						</ul>
					</div>
					<div className="col s2 offset-s4">
						<div className={ehidden}>
							<a className=" btn-floating btn-large waves-effect waves-light orange" href={config.baseUrl+"/patient/edit/"+this.props.medical_record_number}><i className="material-icons">mode_edit</i></a>
							<span>&nbsp;&nbsp;Edit Patient</span>
						</div>
					</div>
				</div>

				<hr />

				<div className="row">
					<div className="col s12">
						<h4>Pressure Injury Summary</h4>
						<table className="centered bordered">
							<thead>
								<tr>
									<th>Location</th>
									<th>Occurrence</th>
									<th>Stage</th>
									<th>Outcome</th>
								</tr>
							</thead>
							<tbody>
								{this.state.body_locations}
							</tbody>
						</table>
					</div>
				</div>

				<hr />

				<div className="row">
					<div className="col s6">
						<h4>Patient Activation Status</h4>
						<table className="centered bordered">
							<thead>
								<tr>
									<th>Status</th>
									<th>Date</th>
									<th>Time</th>
									<th>Reason</th>
								</tr>
							</thead>
							<tbody>
								{this.state.activations}
							</tbody>
						</table>

					</div>
				</div>

				<form id="patient-outcome-form" className={hide_form}>
					<div className={"row "+hide_form}>
						<div className="col s6">
							<h4>Inactivate Patient</h4>
						</div>
					</div>

					<div className="row">
						<div className="input-field col m3 s6">
							<input name="occurred_date" id="occurred_date" type="date" ref={function(ref){if(!self.dates){self.dates = []} self.dates.push(ref)}} value={this.state.occurred_date} onChange={this.onChange} required/>
							<label htmlFor="occurred_date" className="active">Date of Inactivation<span className="red-text"> * </span></label>
						</div>
					</div>
					<div className="row">
						<div className="col s12 input-field">
							<input className="time-input" placeholder="hour" name="occurred_hour" id="occurred_hour" type="number" min="0" max="23" value={this.state.occurred_hour} onChange={this.onChange} required/>:<input className="time-input" placeholder=" min" name="occurred_minute" id="occurred_minute" type="number" min="0" max="59" value={this.state.occurred_minute} onChange={this.onChange} required/>
							<label htmlFor="occurred_hour" className="active">Time of Inactivation<span className="red-text"> * </span></label>
						</div>
					</div>

					<div className="row">
						<div className="input-field col s12">
							<select name="reason" id="reason" value={this.state.reason} defaultValue={this.state.reason} required>
								<option value="">Choose a reason</option>
								<option value="Transferred to Home">Transferred to Home</option>
								<option value="Transferred to Nursing Home">Transferred to Nursing Home</option>
								<option value="Transferred to LTAC">Transferred to LTAC</option>
								<option value="Transferred to Other Unit">Transferred to Other Unit</option>
								<option value="Transferred to Other Hospital">Transferred to Other Hospital</option>
								<option value="Discontinued Use by Patient/Family">Discontinued Use by Patient/Family</option>
								<option value="Discontinued Use by Caregiver">Discontinued Use by Caregiver</option>
								<option value="Discontinued Use by Doctor">Discontinued Use by Doctor</option>
								<option value="Discontinued Use by Digital Health Solutions">Discontinued Use by Digital Health Solutions</option>
								<option value="Deceased">Deceased</option>
								<option value="Other">Other - add Notes</option>
							</select>
							<label>Reason for Inactivation<span className="red-text"> * </span></label>
						</div>
					</div>

					<div className={"row "+other_reason_hidden}>
						<div className="input-field col s12">
							<input name="other_inactivation_reason" id="other_inactivation_reason" type="text" value={this.state.other_inactivation_reason} onChange={this.onChange}/>
							<label htmlFor="other_inactivation_reason" className="active">Please provide reason for inactivation<span className="red-text"> * </span></label>
						</div>
					</div>

					<div className="row">
						<div className="col s12 sensors-returned-question">
							Have all sensors been given to the designated staff?<span className="red-text"> * </span>
						</div>
						<div className="input-field col s3">
							<select name="sensors_collected" id="sensors_collected" value={this.state.sensors_collected} defaultValue={this.state.sensors_collected} required>
								<option value="">?</option>
								<option value="yes">Yes</option>
								<option value="no">No</option>
							</select>
						</div>
					</div>

					<div className={"row "+reason_hidden}>
						<div className="input-field col s12">
							<input name="sensors_not_collected_reason" id="sensors_not_collected_reason" type="text" value={this.state.sensors_not_collected_reason} onChange={this.onChange}/>
							<label htmlFor="sensors_not_collected_reason" className="active">Reason sensors were not returned<span className="red-text"> * </span></label>
						</div>
					</div>

					<div className="row">
						<button id="submit_button" className="btn waves-effect waves-light" type="submit" name="action" disabled={cannot_submit}>Update
							<i className="material-icons right">assignment_ind</i>
						</button>
					</div>
					<span><span className="red-text"> * </span> Indicates the field is required</span>
				</form>
			</section>
		);
	}
});

export default PatientOutcome;

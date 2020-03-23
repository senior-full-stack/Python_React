import React from 'react';
import Config from './Config';
import {BatteryUtils} from './Utils';

var config = new Config();
var $ = window.jQuery = require('jquery');
$.tablesorter = require('tablesorter');


var PatientBodyLocationForm = React.createClass({
	getInitialState: function() {

		var is_default = false;
		if(this.props.medical_record_number == "default") {
			is_default = true;
		}
		return {
			is_default: is_default,
			body_location: this.props.body_location,
			battery_level_indicator: "Not Available",
		};
	},

	onSubmit: function(event) {
		event.preventDefault();
		var self = this;
		var url = "/api/"+config.APIVersion+"/patients/"+this.props.medical_record_number+"/bodylocations/"+this.props.body_location;
		if(this.props.medical_record_number == "default") {
			url = "/api/"+config.APIVersion+"/default/bodylocations/"+this.props.body_location;
		}
		self.setState({
		});
		var method = 'PUT'; //for an existing patient

		var json_out = {};
		json_out = this.state;
		delete json_out.sensor_serial;

		var mrn = this.state.medical_record_number;
		//console.log("submit "+JSON.stringify(json_out));
		$.ajax(
			{
				type: method,
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

			var dl = "/patient/edit/"+self.props.medical_record_number;
			if(self.props.medical_record_number == "default") {
				dl = config.baseUrl+"/devices/defaults";
			}
			Materialize.toast('Settings successfully updated', 4000, 'rounded');

			//send outcome refresh event
			$(document).trigger("refresh-outcome");
		});
	},

	doInit: function(event) {
		if(this.props.medical_record_number !== "undefined") {
			//do ajax call to get all user stuffs
			var self = this;
			var url = "/api/"+config.APIVersion+"/patients/"+this.props.medical_record_number+"/bodylocations/"+this.props.body_location;
			if(this.props.medical_record_number == "default") {
				url = "/api/"+config.APIVersion+"/default/bodylocations/"+this.props.body_location;
			}
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

				//data = data.BodyLocations[0];

				var sensor_serial = "No sensor assigned";
				var battery_level_indicator = "Not Available";
				if(data.sensor_serial && data.sensor_serial != "no sensor assigned") {
					sensor_serial = data.sensor_serial;
					if(data.battery !=0  && !data.stopped) {
						var bp = BatteryUtils.battery_percentage(data.battery);
						battery_level_indicator = <span className={bp.color}>{bp.text}</span>
					}

					// send the event to make the tab of that body location bold
					var event = new CustomEvent(
						"sensor_active_tab", 
						{
							detail: {
								body_location: self.props.body_location,
							},
							bubbles: true,
							cancelable: true
						}
					);
					window.dispatchEvent(event);
				}

				self.setState({
					sensor_serial: sensor_serial,
					gender: data.gender,
					alarm_threshold_minutes: data.alarm_threshold_minutes,
					alarm_clear_multiple: data.alarm_clear_multiple,
					is_wound: data.is_wound,
					wound_stage: data.wound_stage,
					wound_outcome: data.wound_outcome,
					wound_acquisition: data.wound_acquisition,
					existing_wound: data.existing_wound,
					wound_existing_since: data.wound_existing_since,
					wound_measurement: data.wound_measurement,
					site_assessment: data.site_assessment,
					sensor_removal: data.sensor_removal,
					battery_level_indicator: battery_level_indicator,
				});
				$.setup_pickadate(self);
			});
		}
	},

	checkCheckboxes: function(target_location, from) {
		var target = "";
		if(target_location) {
			target = "#"+target_location.replace("bodylocation-","")+" ";
		}
		//console.log(target);
		if(this.state.is_wound || this.state.is_default) {
			$(target+"[name='is_wound']").prop("checked",true);
			//console.log(target);
			$(target+".wound_options :input").each(function(){
				var v = $(this);
				v.prop('disabled', false);
				//console.log(target+" checked is_wound enabled");
			});
		}
		else {
			$(target+"[name='is_wound']").prop("checked", false);
			$(target+".wound_options :input").each(function(){
				var v = $(this);
				v.prop('disabled', true);
				//console.log(target+" checked is_wound disabled");
			});
		}
		if(this.state.existing_wound) {
			$(target+"[name='existing_wound']").prop("checked",true);
			//console.log(target);
			$(target+'.existing_wound_options :input').each(function(){
				var v = $(this);
				v.prop('disabled', false);
			});
		}
		else {
			$(target+"[name='existing_wound']").prop("checked", false);
			$(target+'.existing_wound_options :input').each(function(){
				var v = $(this);
				v.prop('disabled', true);
			});
		}
	},

	onChange: function(e, ee) {
		var self = this;
		var x = $(e.target).attr('id');
		this.state[x] = e.target.value;
		//console.log("onchange bl "+this.state.body_location);
		if(x.endsWith("is_wound")) {
			var y = x.replace(this.state.body_location.toLowerCase()+"_","");
			this.state[y] = $(e.target).prop("checked");
			//console.log("iswound: "+this.state[y]);
			self.checkCheckboxes(this.props.body_location.toLowerCase(), "onchange");
		}
		if(x.endsWith("existing_wound")) {
			var y = x.replace(this.state.body_location.toLowerCase()+"_","");
			this.state[y] = $(e.target).prop("checked");
			//console.log("iswound: "+this.state[y]);
			self.checkCheckboxes(this.props.body_location.toLowerCase(), "onchange");
		}
		this.setState(this.state);
		//console.log('did onchange '+x+" "+e.target.value);
		$('select').material_select();
	},

	componentDidUpdate: function() {
		this.checkCheckboxes(this.props.body_location.toLowerCase(), "didupdate");

		//needed for materialize to render the select forms
		$("#"+this.props.body_location.toLowerCase()+' select').material_select();
		// for HTML5 "required" attribute
		$("#"+this.props.body_location.toLowerCase()+" select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
	},

	componentDidMount: function() {
		var self = this;
		this.doInit();
		//needed for materialize to render the select forms
		$("#"+this.props.body_location.toLowerCase()+' select').material_select();
		$("#"+this.props.body_location.toLowerCase()+' select').on('change', this.onChange);
		// for HTML5 "required" attribute
		$("#"+this.props.body_location.toLowerCase()+" select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
		$("#"+this.props.body_location.toLowerCase()+" #bodylocation-form").on('submit', this.onSubmit);
		self.checkCheckboxes(this.props.body_location.toLowerCase(), "last of didmount");
	},

	render: function() {

		var self = this;
		this.dates = [];

		var submit_text = "Update Body Location";

		var hide_for_default = "";
		if(this.state.is_default) {
			hide_for_default = "hide";
		}

		return (
			<section className="bodylocation">

				<div className="row">
					<form className="col s12" id="bodylocation-form">
						<div className={hide_for_default}>
							<div className="row">
								<div className="input-field col s12">
									<input readOnly name="sensor_serial" id="sensor_serial" type="text" value={this.state.sensor_serial}  required/>
									<label htmlFor="sensor_serial" className={ (this.state.sensor_serial) ? "active" : null}>Sensor Serial</label>
								</div>
							</div>
						</div>

						<div className="row">
							<div className="input-field col s6">
								<span>Sensor Battery:</span>
							</div>
							<div className="input-field col s6 pull-s4">
								<div id="battery_level">{this.state.battery_level_indicator}</div>
							</div>
						</div>

						<div className="row">
							<div className="input-field col s6">
								<input name="alarm_threshold_minutes" id="alarm_threshold_minutes" type="number" step="any" className="validate" value={this.state.alarm_threshold_minutes} onChange={this.onChange} required/>
								<label htmlFor="alarm_threshold_minutes" className={ (this.state.alarm_threshold_minutes) ? "active" : null}>Alarm Threshold (minutes)</label>
							</div>
						</div>

						<div className="row">
							<div className="input-field col s6">
								<input name="alarm_clear_multiple" id="alarm_clear_multiple" type="number" step="any" className="validate" value={this.state.alarm_clear_multiple} onChange={this.onChange} required/>
								<label htmlFor="alarm_clear_multiple" className={ (this.state.alarm_clear_multiple) ? "active" : null}>Alarm Clear Multiple (x Threshold)</label>
							</div>
						</div>

						<div className={hide_for_default}>
							<div className="row">
								<div className="col m6 s12">
									<p>
										<input type="checkbox" id={this.props.body_location.toLowerCase()+"_is_wound"} name="is_wound" value={this.state.is_wound} onChange={this.onChange}/>
										<label htmlFor={this.props.body_location.toLowerCase()+"_is_wound"}>Body Location has a wound</label>
									</p>
								</div>
							</div>

						</div>
						<div id="wound_options" className="wound_options">

							<div className={hide_for_default}>
								<div className="row">
									<div className="input-field col m3 s6">
										<select name="wound_stage" id="wound_stage" value={this.state.wound_stage}>
											<option value="">Choose wound stage</option>
											<option value="1">Stage 1</option>
											<option value="2">Stage 2</option>
											<option value="3">Stage 3</option>
											<option value="4">Stage 4</option>
											<option value="dti">DTI</option>
											<option value="unstageable">Unstageable</option>
											<option value="medical_device_injury">Medical Device Injury</option>
											<option value="mucosal">Mucosal</option>
										</select>
										<label>Wound Stage</label>
									</div>
								</div>

								<div className="row">
									<div className="input-field col m6 s12">
										<input name="wound_measurement" id="wound_measurement" className="validate" value={this.state.wound_measurement} onChange={this.onChange} />
										<label htmlFor="wound_measurement" className={ (this.state.wound_measurement) ? "active" : null}>Wound dimensions L x W x D (cm)</label>
									</div>
								</div>

								<div className="row">
									<div className="col m3 s12">
										<p>
											<input type="checkbox" id={this.props.body_location.toLowerCase()+"_existing_wound"} name="existing_wound" value={this.state.existing_wound} onChange={this.onChange}/>
											<label htmlFor={this.props.body_location.toLowerCase()+"_existing_wound"}>Existing wound</label>
										</p>
									</div>
								</div>

								<div id="existing_wound_options" className="existing_wound_options">
									<div className="row">
										<div className="input-field col m3 s6">
											<input name="wound_existing_since" ref={function(ref){if(!self.dates){self.dates = []} self.dates.push(ref)}} className="datepicker" type="date" id="wound_existing_since" value={this.state.wound_existing_since} onChange={this.onChange} required/>
											<label htmlFor="wound_existing_since" className="active">Existing wound since</label>
										</div>
									</div>
								</div> {/* end existing_wound_options */}

								<div className="row">
									<div className="input-field col m3 s12">
										<select name="wound_acquisition" id="wound_acquisition" value={this.state.wound_acquisition}>
											<option value="">Choose how wound acquired</option>
											<option value="present_on_admission">Present on admission</option>
											<option value="facility_acquired">Facility Acquired</option>
											<option value="unknown">Unknown</option>
										</select>
										<label>Wound Acquired</label>
									</div>
								</div>

								<div className="row">
									<div className="input-field col m3 s12">
										<select name="wound_outcome" id="wound_outcome" value={this.state.wound_outcome}>
											<option value="">Choose wound outcome</option>
											<option value="na">N/A</option>
											<option value="healing">Healing</option>
											<option value="healed">Healed</option>
											<option value="no_change">No Change</option>
											<option value="worsening">Worsening</option>
										</select>
										<label>Wound Outcome</label>
									</div>
								</div>
							</div> {/* end wound_options */}
						</div>

						<div className="row">
							<div className="input-field col s12">
								<input name="site_assessment" id="site_assessment" type="text" className="validate" value={this.state.site_assessment} onChange={this.onChange}/>
								<label htmlFor="site_assessment" className={ (this.state.site_assessment) ? "active" : null}>Site assessment</label>
							</div>
						</div>

						<div className="row">
							<div className="input-field col s12">
								<input name="sensor_removal" id="sensor_removal" type="text" className="validate" value={this.state.sensor_removal} onChange={this.onChange}/>
								<label htmlFor="sensor_removal" className={ (this.state.sensor_removal) ? "active" : null}>Reason for removal</label>
							</div>
						</div>

						<div className="row">
							<button id="bodylocation-submit" className="btn waves-effect waves-light" type="submit" name="action">{submit_text}
								<i className="material-icons right">assignment_ind</i>
							</button>
						</div>

					</form>
				</div>

			</section>
		);
	}
});

export default PatientBodyLocationForm;

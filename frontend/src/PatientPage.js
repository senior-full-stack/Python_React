import React from 'react';
import PatientForm from './PatientForm';
import PatientOutcome from './PatientOutcome';
import PatientBodyLocationForm from './PatientBodyLocationForm';

var $ = window.jQuery = require('jquery');
$.tablesorter = require('tablesorter');

var PatientPage = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
			users: <tr><td>No patients.</td></tr>,
		};
	},

	handleSensorActiveTab: function(e) {
		var body_loc = e.detail.body_location.toLowerCase();
		var newstate = {}
		newstate[body_loc+"_style"] = {"fontWeight": "bold"};
		this.setState(newstate);
	},

	componentDidMount: function() {
		$('ul.tabs').tabs();
		window.addEventListener('sensor_active_tab', this.handleSensorActiveTab);
	},

	componentWillUnmount: function() {
		window.removeEventListener('sensor_active_tab', this.handleSensorActiveTab);
	},

	componentDidUpdate: function() {
		$('ul.tabs').tabs();
	},

	render: function() {
		var first_option = <div id="first_option" className="col s12"><PatientForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} edit={true}/></div>;
		var first_option_title = "Patient Info";

		if(this.props.is_default) {
			first_option = <div id="first_option" className="col s12"><DeviceForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} edit={true}/></div>;
			first_option_title = "Default Device Settings";
		}

		//check screen width, tocompensate for large screen
		var lg_screen = "";
		var body = document.getElementsByTagName('body')[0];
    var width = window.innerWidth || document.documentElement.clientWidth || body.clientWidth;
		var w = parseInt(width);
		if(w < 980){
			lg_screen = " col s3";
		}
		else {
			lg_screen = "";
		}

		return (
			<section>
				<div className="row">
					<span id="patient_page_patient_name"></span>
					<span id="patient_page_patient_mrn"></span>
					<div className="col s12" id="patient-tabs">
						<ul className="tabs">
							<li className={"tab"+lg_screen}><a href="#first_option">{first_option_title}</a></li>
							<li className={"tab"+lg_screen}><a style={this.state.skull_style} href="#skull" data-tab_id="bodylocation-skull">Skull</a></li>
							<li className={"tab"+lg_screen}><a style={this.state.upper_spine_style} href="#upper_spine" data-tab_id="bodylocation-upper_spine">Upper Spine</a></li>
							<li className={"tab"+lg_screen}><a style={this.state.sacrum_style} href="#sacrum" data-tab_id="bodylocation-sacrum">Sacrum</a></li>
							<li className={"tab"+lg_screen}><a style={this.state.left_hip_style} href="#left_hip" data-tab_id="bodylocation-left_hip">Left Hip</a></li>
							<li className={"tab"+lg_screen}><a style={this.state.right_hip_style} href="#right_hip" data-tab_id="bodylocation-right_hip">Right Hip</a></li>
							<li className={"tab"+lg_screen}><a style={this.state.left_ischia_style} href="#left_ischia" data-tab_id="bodylocation-left_ischia">Left Ischia</a></li>
							<li className={"tab"+lg_screen}><a style={this.state.right_ischia_style} href="#right_ischia" data-tab_id="bodylocation-right_ischia">Right Ischia</a></li>
							<li className={"tab"+lg_screen}><a style={this.state.left_elbow_style} href="#left_elbow" data-tab_id="bodylocation-left_elbow">Left Elbow</a></li>
							<li className={"tab"+lg_screen}><a style={this.state.right_elbow_style} href="#right_elbow" data-tab_id="bodylocation-right_elbow">Right Elbow</a></li>
							<li className={"tab"+lg_screen}><a style={this.state.left_heel_style} href="#left_heel" data-tab_id="bodylocation-left_heel">Left Heel</a></li>
							<li className={"tab"+lg_screen}><a style={this.state.right_heel_style} href="#right_heel" data-tab_id="bodylocation-right_heel">Right Heel</a></li>
							<li className={"tab"+lg_screen}><a href="#outcome" data-tab_id="bodylocation-right_heel">Outcome</a></li>
						</ul>
					</div>
					{first_option}
					<div id="skull" className="col s12"><PatientBodyLocationForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} body_location="SKULL" edit={true}/></div>
					<div id="upper_spine" className="col s12"><PatientBodyLocationForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} body_location="UPPER_SPINE" edit={true}/></div>
					<div id="sacrum" className="col s12"><PatientBodyLocationForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} body_location="SACRUM" edit={true}/></div>
					<div id="left_hip" className="col s12"><PatientBodyLocationForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} body_location="LEFT_HIP" edit={true}/></div>
					<div id="right_hip" className="col s12"><PatientBodyLocationForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} body_location="RIGHT_HIP" edit={true}/></div>
					<div id="left_ischia" className="col s12"><PatientBodyLocationForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} body_location="LEFT_ISCHIA" edit={true}/></div>
					<div id="right_ischia" className="col s12"><PatientBodyLocationForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} body_location="RIGHT_ISCHIA" edit={true}/></div>
					<div id="left_elbow" className="col s12"><PatientBodyLocationForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} body_location="LEFT_ELBOW" edit={true}/></div>
					<div id="right_elbow" className="col s12"><PatientBodyLocationForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} body_location="RIGHT_ELBOW" edit={true}/></div>
					<div id="left_heel" className="col s12"><PatientBodyLocationForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} body_location="LEFT_HEEL" edit={true}/></div>
					<div id="right_heel" className="col s12"><PatientBodyLocationForm is_default={this.props.is_default} medical_record_number={this.props.medical_record_number} body_location="RIGHT_HEEL" edit={true}/></div>
					<div id="outcome" className="col s12"><PatientOutcome medical_record_number={this.props.medical_record_number} edit_hidden={true}/></div>
				</div>
			</section>
		);
	}
});
export default PatientPage;

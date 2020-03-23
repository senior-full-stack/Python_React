import React from 'react';
import Config from './Config';

import DeviceForm from './DeviceForm';
import PatientBodyLocationForm from './PatientBodyLocationForm';

var config = new Config();
var $ = window.jQuery = require('jquery');

var DevicePage = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
		};
	},

	componentDidMount: function() {
		$('ul.tabs').tabs();
	},

	componentWillUnmount: function() {
	},

	componentDidUpdate: function() {
		$('ul.tabs').tabs();
	},

	render: function() {
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
				<span id="patient_page_patient_name">Default Device Settings</span>
				<div className="row">
					<div className="col s12" id="patient-tabs">
						<ul className="tabs">
							<li className={"tab"+lg_screen}><a href="#device_settings">Device</a></li>
							<li className={"tab"+lg_screen}><a href="#skull" data-tab_id="bodylocation-skull">Skull</a></li>
							<li className={"tab"+lg_screen}><a href="#upper_spine" data-tab_id="bodylocation-upper_spine">Upper Spine</a></li>
							<li className={"tab"+lg_screen}><a href="#sacrum" data-tab_id="bodylocation-sacrum">Sacrum</a></li>
							<li className={"tab"+lg_screen}><a href="#left_hip" data-tab_id="bodylocation-left_hip">Left Hip</a></li>
							<li className={"tab"+lg_screen}><a href="#right_hip" data-tab_id="bodylocation-right_hip">Right Hip</a></li>
							<li className={"tab"+lg_screen}><a href="#left_ischia" data-tab_id="bodylocation-left_ischia">Left Ischia</a></li>
							<li className={"tab"+lg_screen}><a href="#right_ischia" data-tab_id="bodylocation-right_ischia">Right Ischia</a></li>
							<li className={"tab"+lg_screen}><a href="#left_elbow" data-tab_id="bodylocation-left_elbow">Left Elbow</a></li>
							<li className={"tab"+lg_screen}><a href="#right_elbow" data-tab_id="bodylocation-right_elbow">Right Elbow</a></li>
							<li className={"tab"+lg_screen}><a href="#left_heel" data-tab_id="bodylocation-left_heell">Left Heel</a></li>
							<li className={"tab"+lg_screen}><a href="#right_heel" data-tab_id="bodylocation-right_heel">Right Heel</a></li>
						</ul>
					</div>
					<div id="device_settings" className="col s12"><DeviceForm device_id={this.props.device_id} edit={true}/></div>
					<div id="skull" className="col s12"><PatientBodyLocationForm medical_record_number={this.props.medical_record_number} body_location="SKULL" edit={true}/></div>
					<div id="upper_spine" className="col s12"><PatientBodyLocationForm medical_record_number={this.props.medical_record_number} body_location="UPPER_SPINE" edit={true}/></div>
					<div id="sacrum" className="col s12"><PatientBodyLocationForm medical_record_number={this.props.medical_record_number} body_location="SACRUM" edit={true}/></div>
					<div id="left_hip" className="col s12"><PatientBodyLocationForm medical_record_number={this.props.medical_record_number} body_location="LEFT_HIP" edit={true}/></div>
					<div id="right_hip" className="col s12"><PatientBodyLocationForm medical_record_number={this.props.medical_record_number} body_location="RIGHT_HIP" edit={true}/></div>
					<div id="left_ischia" className="col s12"><PatientBodyLocationForm medical_record_number={this.props.medical_record_number} body_location="LEFT_ISCHIA" edit={true}/></div>
					<div id="right_ischia" className="col s12"><PatientBodyLocationForm medical_record_number={this.props.medical_record_number} body_location="RIGHT_ISCHIA" edit={true}/></div>
					<div id="left_elbow" className="col s12"><PatientBodyLocationForm medical_record_number={this.props.medical_record_number} body_location="LEFT_ELBOW" edit={true}/></div>
					<div id="right_elbow" className="col s12"><PatientBodyLocationForm medical_record_number={this.props.medical_record_number} body_location="RIGHT_ELBOW" edit={true}/></div>
					<div id="left_heel" className="col s12"><PatientBodyLocationForm medical_record_number={this.props.medical_record_number} body_location="LEFT_HEEL" edit={true}/></div>
					<div id="right_heel" className="col s12"><PatientBodyLocationForm medical_record_number={this.props.medical_record_number} body_location="RIGHT_HEEL" edit={true}/></div>
				</div>

			</section>
		);
	}
});

export default DevicePage;

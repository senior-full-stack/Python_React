import React from 'react';
import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');

var moment = require('moment');

var Device = React.createClass({
  getInitialState: function() {
    return {
      time_type: 'relative',
			show_time: moment(this.props.last_seen).fromNow(),
    };
  },

	toggleTime: function() {
		if(this.state.time_type == "relative") {
			this.setState({
				time_type: 'absolute',
				show_time: moment(this.props.last_seen).format('MMMM Do YYYY, h:mm:ss a')
			});
		}
		else {
			this.setState({
				time_type: 'relative',
				show_time: moment(this.props.last_seen).fromNow()
			});
		}
	},

	componentDidMount: function() {
		$('.dropdown-button').dropdown({
			inDuration: 300,
			outDuration: 225,
			constrain_width: false, // Does not change width of dropdown to that of the activator
			gutter: 0, // Spacing from edge
			belowOrigin: false, // Displays dropdown below the button
			alignment: 'left' // Displays dropdown with edge aligned to the left of button
		})
	},

	render: function() {

		var self = this;

		var mrn_row = <div>
						<a className='dropdown-button btn orange' href='#' data-activates={'dropdown-'+self.props.name}>Assign to a patient</a>
						<ul id={'dropdown-'+self.props.name} className='dropdown-content'>
							{
								this.props.unassigned_patients.map(function(patient) {
									return <li key={self.props.name+"-"+patient.medical_record_number}><a className="assign-link" data-medical_record_number={patient.medical_record_number} data-device_serial={self.props.name} href="#!">{patient.name + ' ' + patient.last_name}</a></li>;
								})
							}
						</ul>
					</div>;

		if(this.props.medical_record_number) {
			mrn_row = <span><strong>Patient Name: </strong>{this.props.patient_name}&nbsp;&nbsp;<a className="btn-floating waves-effect waves-light red unassign-button" data-medical_record_number={this.props.medical_record_number} data-device_serial={this.props.name}><i className="material-icons right">remove_circle</i></a>&nbsp;Unassign</span>;
		}
		
		var delete_device;
		if(this.props.current_user.role == "admin") {
			delete_device = <td className="delete"><a className="btn-name waves-light delete-click" data-device_serial={this.props.name}><i className="material-icons right red-text">delete</i></a></td>
		}

		return(
				<tr>
					<td><a href={"/devices/"+this.props.name} > {this.props.name}</a></td>
					<td className="last_seen" onClick={this.toggleTime}>{this.state.show_time}</td>
					<td className="mrn">{mrn_row}</td>
					{delete_device}
				</tr>
				);
	},

});

export default Device;

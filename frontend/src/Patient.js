import React from 'react';
import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');
$.tablesorter = require('tablesorter');

var Patient = React.createClass({
	getInitialState: function() {
		return {
			//time_type: 'relative',
			//show_time: moment(this.props.last_seen).fromNow(),
		};
	},

	render: function() {

		var delete_patient;
		if(this.props.current_user.role == "admin") {
			delete_patient = <td className="delete"><a className="btn-name waves-light delete-click" data-medical_record_number={this.props.medical_record_number}><i className="material-icons red-text">delete</i></a></td>
		}

		return(
			<tr>
				<td><a href={config.baseUrl+"/patient/edit/"+this.props.medical_record_number}>{this.props.name}</a></td>
				<td>{this.props.device_assigned}</td>
				<td><a href={config.baseUrl+"/patient/timeline/"+this.props.medical_record_number}>View Timeline</a></td>
				<td><a href={config.baseUrl+"/patient/reports/"+this.props.medical_record_number}>View Reports</a></td>
				<td><a href={config.baseUrl+"/patient/outcome/"+this.props.medical_record_number}>Outcome</a></td>
				<td>{this.props.activation_status}</td>
				{delete_patient}
			</tr>
		);
	},

});

// add parser through the tablesorter addParser method 
$.tablesorter.addParser({ 
	// set a unique id 
	id: 'activations', 
	is: function(s) { 
		// return false so this parser is not auto detected 
		return false; 
	}, 
	format: function(s) { 
		// format your data for normalization 
		return s.toLowerCase().replace(/^activated/,2).replace(/^reactivated/,1).replace(/inactivated/,0); 
	}, 
	// set type, either numeric or text 
	type: 'numeric' 
}); 


export default Patient;

import React from 'react';

import Patient from './Patient';

import Config from './Config';

var config = new Config();

var Patients = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
			patients: '',
			loading: <div className="progress">
				<div className="indeterminate"></div>
			</div>,
		};
	},

	onSubmit: function(event) {
		var self = this;
		var url = "/api/"+config.APIVersion+"/patients";
		self.setState({
			state: 'looking up patients...',
			patients: self.state.patients
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
		).done(function(data){
			self.setState({
				state: 'idle',
				loading: '',
				patients: data.patients.map(function(patient){

					var device_serial = "No device assigned";
					// TODO: shouldn't be array of devices, only one
					if(patient.device[0] && patient.device[0].name) {
						device_serial = patient.device[0].name;
					}
					return (<Patient key={patient.id} medical_record_number={patient.medical_record_number} device_assigned={device_serial} name={patient.name + ' ' + patient.last_name} activation_status={patient.activation_status} current_user={self.props.current_user}/>);
				})
			});
			$("#patients-table").tablesorter({ 
				headers: { 
					6: { 
						sorter:'activations' 
					} 
				}, 
				sortList: [[6,1], [1,0]]
			}); 

			$(".delete-click").click(function() {
					var confirmed = confirm("Are you sure you want to delete this patient?");
					if(confirmed !== true)	{
						return;
					}
					var el = $(this);
					var mrn = el.attr("data-medical_record_number");
					var url = "/api/"+config.APIVersion+"/patients/"+mrn+"/";
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
							//redirect back to patients
							window.location.href = config.baseUrl+"/patients";
						});
				});
		});
	},

	componentDidMount: function() {
		this.onSubmit();
	},

	componentDidUpdate: function() {
		//this.onSubmit();
	},
	
	componentWillUnmount: function() {
		$(".delete-click").unbind("click");
	},

	render: function() {
		var delete_header;
		if(this.props.current_user.role == "admin") {
			delete_header = <th data-field="delete">Delete</th>
		}
		return (
			<section>
				<table id="patients-table" className="a-table">
					<thead>
						<tr>
							<th data-field="medical_record_number">Patient Name or Identifier</th>
							<th data-field="assigned_device">Assigned Device</th>
							<th data-field="view_timeline">Timeline</th>
							<th data-field="view_reports">Reports</th>
							<th data-field="view_outcome">Outcome</th>
							<th data-field="status">Status</th>
							{delete_header}
						</tr>
					</thead>
					<tbody>
						{this.state.patients}
					</tbody>
				</table>
				<div className="top-right-button">
					<a className="btn-floating btn-large waves-effect waves-light red" href={config.baseUrl+"/patient/new"}><i className="material-icons">add</i></a>
					<span>Add a patient</span>
				</div>
				{this.state.loading}
			</section>
		);
	}
});


export default Patients;

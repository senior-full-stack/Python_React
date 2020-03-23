import React from 'react';
import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');

var AdminSettings = React.createClass({
	getInitialState: function() {
		return {
			available_unit_floors: [],
			new_unit: "",
		};
	},

	onChange: function(e, ee) {
		var x = $(e.target).attr('id');
		this.state[x] = e.target.value;
		this.setState(this.state);
	},

	onSubmit: function(event) {
		var self = this;
		var url = "/api/"+config.APIVersion+"/admin";
		var method = "PUT";

		var json_out = {};
		
		json_out.unit_floor = JSON.stringify(this.state.available_unit_floors);

		$.ajax(
			{
				url: url,
				type: method,
				contentType: 'application/json; charset=UTF-8', 
				dataType: 'json',
				data: JSON.stringify(json_out),
				beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}
		).done(function(data){
				Materialize.toast("Successfully updated admin settings", 2000, 'rounded');
		});
	},

	componentDidMount: function() {
		var self = this;
		var url = "/api/"+config.APIVersion+"/admin";
		$.ajax(
			{
				url: url,
				type: 'GET',
				beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}
		).done(function(data) {
			self.setState({
				available_unit_floors: JSON.parse(data.unit_floor),
			});
		});
	},

	componentDidUpdate: function() {
	},

	deleteUnit: function(e) {
		var target_unit = $(e.target).attr("data-unit_name");
		var confirmed = confirm("Are you sure you want to delete the '"+target_unit+"' unit/floor?");
		if(confirmed !== true)	{
			return;
		}
		// remove it from the list
		var u_idx = this.state.available_unit_floors.indexOf(target_unit);
		if (u_idx > -1) {
			this.state.available_unit_floors.splice(u_idx, 1);
		}
		this.setState(this.state);
		this.onSubmit();
	},

	addUnit: function(e) {
		this.state.available_unit_floors.push(this.state.new_unit);
		this.state.available_unit_floors.sort();
		this.state.new_unit = "";
		this.setState(this.state);
		this.onSubmit();
	},

	render: function() {
		var self = this;

		var unit_floor_list = this.state.available_unit_floors.map(function(u_name, index){
			return <li key={index+"-"+u_name} className="collection-item"><div>{u_name}<a href="#" onClick={function(event){self.deleteUnit(event)}} className="secondary-content"><i className="material-icons red-text" data-unit_name={u_name}>delete</i></a></div></li>
		});

		return (
			<section className="admin-settings">
				<h2>Admin settings</h2>
					<div>
						<a className="btn-floating btn waves-effect waves-light blue" href={config.baseUrl+"/devices/defaults"}><i className="material-icons">settings</i></a>
						<span>&nbsp;Default Device Settings</span>
				</div>
				<div className="row">
					<ul className="collection with-header">
						<li className="collection-header"><h4>Available Units/Floors</h4></li>
						{unit_floor_list}
						<li className="collection-item">
							<div className="input-field col s4">
								<input ref="new_unit" type="text" id="new_unit" name="new_unit" value={this.state.new_unit} onChange={this.onChange}/>
								<label htmlFor="new_unit">New Unit</label>
							</div>
							<br />
							<a href="#" onClick={function(event){self.addUnit(event)}} className={"secondary-content "+(self.state.new_unit.length>0 ? null: "hide")}>
								Add <i className="material-icons gree-text">add</i>
							</a>
						</li>
					</ul>
				</div>
			</section>
		);
	}
});

export default AdminSettings;

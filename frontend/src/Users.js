import React from 'react';

import User from './User';

import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');
$.tablesorter = require('tablesorter');

var Users = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
			users: '',
			loading: <div className="progress">
				<div className="indeterminate"></div>
			</div>,
		};
	},

	onSubmit: function(event) {
		//event.preventDefault();
		var self = this;
		var url = "/api/"+config.APIVersion+"/users";
		self.setState({
			state: 'looking up users...',
			users: self.state.users
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
				users: data.users.map(function(user){
					return (<User key={user.id} name={user.name} email={user.email} phone_number={user.phone_number} current_user={self.props.current_user}/>);
				}),
				loading: '',
			});
			$("#users-table").tablesorter({ 
				sortList: [[0,0]]
			});

			$(".delete-click").click(function() {
					var confirmed = confirm("Are you sure you want to delete this user?");
					if(confirmed !== true)	{
						return;
					}
					var el = $(this);
					var u = el.attr("data-user_id");
					var url = "/api/"+config.APIVersion+"/users/"+u+"/";
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
							self.onSubmit();
							Materialize.toast('User successfully deleted', 4000, 'rounded');
						});
				});
		});
	},

	componentDidMount: function() {
		this.onSubmit();
	},
	
	componentWillUnmount: function() {
		$(".delete-click").unbind("click");
	},

	render: function() {

		var admin_edit_title;
		if(this.props.current_user.role == "admin") {
			admin_edit_title = <th data-field="edit_user">Edit User</th>;
		}

		var delete_header;
		if(this.props.current_user.role == "admin") {
			delete_header = <th data-field="delete">Delete</th>
		}
		return (
			<section>
				<table id="users-table" className="a-table">
					<thead>
						<tr>
							<th data-field="name">Name</th>
							<th data-field="email">E-mail</th>
							<th data-field="phone_number">Phone Number</th>
							{admin_edit_title}
							{delete_header}
						</tr>
					</thead>
					<tbody>
						{this.state.users}
					</tbody>
				</table>
				<div className="top-right-button">
					<a className="btn-floating btn-large waves-effect waves-light red" href={config.baseUrl+"/user/new"}><i className="material-icons">add</i></a>
					<span>Add new user</span>
				</div>
				{this.state.loading}
			</section>
		);
	}
});

export default Users;

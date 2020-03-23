import React from 'react';
import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');

var User = React.createClass({
	getInitialState: function() {
		return {
			//time_type: 'relative',
			//show_time: moment(this.props.last_seen).fromNow(),
		};
	},

	render: function() {

		var admin_edit_row;
		if(this.props.current_user.role == "admin") {
			admin_edit_row = <td><a href={config.baseUrl+"/users/edit/"+this.props.email}><i className="material-icons">mode_edit</i></a></td>;
		}
		
		var admin_delete_user;
		if(this.props.current_user.role == "admin") {
			admin_delete_user = <td className="delete"><a className="btn-name waves-light red delete-click" data-user_id={this.props.email}><i className="material-icons right">remove_circle</i></a>&nbsp;&nbsp;Delete User</td>
		}

		return(
			<tr>
				<td>{this.props.name}</td>
				<td>{this.props.email}</td>
				<td>{this.props.phone_number}</td>
				{admin_edit_row}
				{admin_delete_user}
			</tr>
		);
	},

});

export default User;

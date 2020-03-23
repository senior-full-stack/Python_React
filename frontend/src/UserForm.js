import React from 'react';
import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');

var UserForm = React.createClass({
	getInitialState: function() {
		return {
			user: {},
			submit_text: "Add user",
			pw_required: true,
			pw_shown: true,
		};
	},

	onChange: function(e, ee) {
		var x = $(e.target).attr('id');
		if($(e.target).is(':checkbox')) {
			this.state.user[x] = $(e.target).prop("checked");
		}
		else {
			this.state.user[x] = e.target.value;
			$('select').material_select();
		}
		this.setState(this.state.user);
	},

	onSubmit: function(event) {
alert('hi')
		debugger;
		var self = this;
		var url = "/api/"+config.APIVersion+"/users";
		var method = "POST";
		if(this.props.user_email == this.props.current_user.email) {
			url = "/api/"+config.APIVersion+"/users/"+this.props.current_user.email;
			method = "PUT";
		}
		else if(this.props.user_email) {
			url = "/api/"+config.APIVersion+"/users/"+this.props.user_email;
			method = "PUT";
		}
		self.setState({
			state: 'adding patient...'
		});

		var json_out = {};

		event.preventDefault();

		if(this.state.pw_required) {
			var p1 = $("#password").val();
			var p2 = $("#password2").val();

			//check for matching passwords
			if(p1 != p2) {
				self.setState({
					password_error: "Passwords must match",
					password2_error: "Passwords must match",
					password_invalid: "invalid",
					password2_invalid: "invalid",
					password_label_class: "active",
					password2_label_class: "active",
				});
				return;
			}

			//ensure password length
			else if(p1.length < 6 || p2.length < 6) {
				self.setState({
					password_error: "Password must be at least 6 characters",
					password2_error: "Password must be at least 6 characters",
					password_invalid: "invalid",
					password2_invalid: "invalid",
					password_label_class: "active",
					password2_label_class: "active",
				});
				return;
			}
		}

		json_out.name = $("#name").val();
		json_out.password = $("#password").val();
		json_out.email = $("#email").val();
		json_out.phone_number = $("#phone_number").val();
		json_out.email_notification = this.state.user.email_notification;
		json_out.role = this.state.user.role;

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
		)
			.done(function(data){
				if(method == 'PUT') {
					Materialize.toast("Successfully updated user", 4000, 'rounded');
				}
				else {
					Materialize.toast('User successfully added', 4000, 'rounded');
					$.navigate(config.baseUrl+"/users");
				}
			});
	},

	componentDidMount: function() {
		var self = this;
		if(!this.props.new_user) {
			var url = "/api/"+config.APIVersion+"/users/"+this.props.user_email;
			if(this.props.user_email) {
				self.setState({
					submit_text: "Update user",
					pw_required: false,
				});
			}
			if(this.props.user_email == this.props.current_user.email) {
				url = "/api/"+config.APIVersion+"/users/"+this.props.current_user.email;
				if(this.props.user_email) {
					self.setState({
						submit_text: "Update user",
						pw_required: false,
						pw_shown: false,
					});
				}
			}
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
			)
				.done(function(data) {
					self.setState({
						user: data
					});
				});
		}

		//needed for materialize to render the select forms
		$('select').material_select();
		$('select').on('change', this.onChange);
		// for HTML5 "required" attribute
		$("select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
		$("#submit_button").on("click", this.onSubmit);
	},

	componentDidUpdate: function() {
		$('select').material_select();
		// for HTML5 "required" attribute
		$("select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
	},

	render: function() {

		var tablet_unplugged_notifications = "";
		if(this.state.user.role == "admin") {
				tablet_unplugged_notifications = <div className="row">
							<div className="input-field col s12">
								<input name="email_notification" id="email_notification" type="checkbox" value={this.state.user.email_notification} onChange={this.onChange} checked={this.state.user.email_notification} />
								<label htmlFor="email_notification" >Received tablet unplugged notifications</label>
							</div>
						</div>
		}

		return (
			<section className="new-user">
				<div className="row">
					<form className="col s12">
						<div className="row">
							<div className="input-field col s12">
								<input name="name" id="name" type="text" className="validate" value={this.state.user.name} onChange={this.onChange} required/>
								<label htmlFor="name" className={ (this.state.user.name) ? "active" : null}>Name</label>
							</div>
						</div>

						<div className={"row "+(this.state.pw_shown ? false : "hide" : "")}>
							<div className="input-field col s12">
								<input id="password" name="password" type="password" className={this.state.password_invalid} required={this.state.pw_required} />
								<label className={this.state.password_label_class} id="password_label" data-error={this.state.password_error} htmlFor="password">Password</label>
							</div>
						</div>

						<div className={"row "+(this.state.pw_shown ? false : "hide" : "")}>
							<div className="input-field col s12">
								<input id="password2" name="password2" type="password" className={this.state.password2_invalid} required={this.state.pw_required} />
								<label className={this.state.password2_label_class} id="password2_label" data-error={this.state.password2_error} htmlFor="password2">Verify Password</label>
							</div>
						</div>

						<div className="row">
							<div className="input-field col s12">
								<input name="email" id="email" type="email" className="validate" value={this.state.user.email} onChange={this.onChange} required/>
								<label htmlFor="email" data-error="E-mail is not valid" className={ (this.state.user.email) ? "active" : null}>E-mail</label>
							</div>
						</div>

						<div className="row">
							<div className="input-field col s4">
								<select name="role" id="role" value={this.state.user.role} onChange={this.onChange} required>
									<option value="">Choose role</option>
									<option value="caregiver">Caregiver</option>
									<option value="admin">Admin</option>
								</select>
								<label>User Role</label>
							</div>
						</div>

						{tablet_unplugged_notifications}

						<div className="row">
							<div className="input-field col s12">
								<input name="phone_number" id="phone_number" type="text" className="validate" value={this.state.user.phone_number} onChange={this.onChange} required/>
								<label htmlFor="phone_number" className={ (this.state.user.phone_number) ? "active" : null}>Phone Number</label>
							</div>
						</div>

						<div className="row">
							<button id="submit_button" className="btn waves-effect waves-light" type="submit" name="action">{this.state.submit_text}
								<i className="material-icons right">assignment_ind</i>
							</button>
						</div>

						<div className={"row "+(this.state.pw_shown ? "hide" : "")}>
							<a href={config.baseUrl+"/my-account/change-password"} className="btn waves-effect waves-light red"><i className="material-icons right">lock</i>Change Password</a>
						</div>
					</form>
				</div>

			</section>
		);
	}
});

var UserPasswordForm = React.createClass({
  getInitialState: function() {
		return {
		};
  },

	onSubmit: function(event) {
    var self = this;
		var url = "/api/"+config.APIVersion+"/users/"+this.props.user_email+"/password";
		var method = "PUT";

		var json_out = {};
		
		event.preventDefault();

		var pold = $("#current_password").val();
		var p1 = $("#password").val();
		var p2 = $("#password2").val();

		//check for matching passwords
		if(p1 != p2) {
			self.setState({
				password_error: "Passwords must match",
				password2_error: "Passwords must match",
				password_invalid: "invalid",
				password2_invalid: "invalid",
				password_label_class: "active",
				password2_label_class: "active",
			});
			return;
		}

		//ensure password length
		else if(p1.length < 6 || p2.length < 6 || pold.length < 6) {
			self.setState({
				current_password_error: "Password must be at least 6 characters",
				current_password_invalid: "invalid",
				current_password_label_class: "active",
				password_error: "Password must be at least 6 characters",
				password2_error: "Password must be at least 6 characters",
				password_invalid: "invalid",
				password2_invalid: "invalid",
				password_label_class: "active",
				password2_label_class: "active",
			});
			return;
		}

		json_out.old_password = $("#current_password").val();
		json_out.new_password = $("#password").val();

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
							navigate(baseUrl+"/logout");
						},
						403: function() {
							self.setState({
								current_password_error: "Password is incorrect",
								current_password_invalid: "invalid",
								current_password_label_class: "active",
							});
						}
					},
				}
				)
				.done(function(data){
						Materialize.toast("Successfully updated password", 4000, 'rounded');
				});
  },

	componentDidMount: function() {
		//this.onSubmit();
		//needed for materialize to render the select forms
	  $('select').material_select();
		// for HTML5 "required" attribute
    $("select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
		$("#submit_button").on("click", this.onSubmit);
	},

  render: function() {
		var submit_text = "Change Password";

    return (
      <section className="change-password">
	<div className="row">
    <form className="col s12">

			<div className="row">
        <div className="input-field col s12">
	        <input id="current_password" name="current_password" type="password" className={this.state.current_password_invalid} required />
          <label className={this.state.current_password_label_class} id="password_label" data-error={this.state.current_password_error} htmlFor="current_password">Current Password</label>
				</div>
      </div>

			<div className="row">
        <div className="input-field col s12">
	        <input id="password" name="password" type="password" className={this.state.password_invalid} />
          <label className={this.state.password_label_class} id="password_label" data-error={this.state.password_error} htmlFor="password">Password</label>
				</div>
      </div>

			<div className="row">
        <div className="input-field col s12">
	        <input id="password2" name="password2" type="password" className={this.state.password2_invalid} />
          <label className={this.state.password2_label_class} id="password2_label" data-error={this.state.password2_error} htmlFor="password2">Verify Password</label>
				</div>
      </div>
      
      <div className="row">
			  <button id="submit_button" className="btn waves-effect waves-light" type="submit" name="action">{submit_text}
    			<i className="material-icons right">lock</i>
			  </button>
      </div>

    </form>
  </div>
        	
			</section>
    );
  }
});


export {UserForm, UserPasswordForm};

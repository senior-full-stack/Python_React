import React from 'react';
import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');

var DeviceForm = React.createClass({
  getInitialState: function() {
		return {
    };
  },

	onSubmit: function(event) {
		event.preventDefault();
    var self = this;
    var url = "/api/"+config.APIVersion+"/devices/"+this.props.device_id;
		if(this.props.device_id == "default") {
    	url = "/api/"+config.APIVersion+"/default/devices/settings";
		}
    self.setState({
    });
		var method = 'PUT'; 

		var json_out = {};
		json_out = this.state;
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
					Materialize.toast('Settings successfully updated', 4000, 'rounded');
				});
  },

	doInit: function(event) {
		var self = this;
		var url = "/api/"+config.APIVersion+"/devices/"+this.props.device_id;
		if(this.props.device_id == "default") {
			url = "/api/"+config.APIVersion+"/default/devices/settings";
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

			self.setState({
				language: data.language,
				alarm_volume: data.alarm_volume,
				alarm_sound: data.alarm_sound,
				alarm_duration: data.alarm_duration,
			});
		});
	},

	onChange: function(e, ee) {
		var x = $(e.target).attr('id');
		this.state[x] = e.target.value;
		this.setState(this.state);
	  $('select').material_select();
	},

	componentDidUpdate: function() {
		var edit = this.props.edit;
		$('#device-form :input').each(function(){
			var v = $(this);
			if(!edit) {
				v.prop('disabled', true);
			}
			else {
				v.prop('disabled', false);
			}
		});
		//needed for materialize to render the select forms
	  $('select').material_select();
		// for HTML5 "required" attribute
    $("select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
	},

	componentDidMount: function() {
		this.doInit();
		var edit = this.props.edit;
		$('#device-form :input').each(function(){
			var v = $(this);
			if(!edit) {
				v.prop('disabled', true);
			}
			else {
				v.prop('disabled', false);
			}
		});
		//needed for materialize to render the select forms
	  $('select').material_select();
	  $('select').on('change', this.onChange);
		// for HTML5 "required" attribute
    $("select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
		$("#device-form").on('submit', this.onSubmit);
	},

  render: function() {

		var title;
		var device_id_row;
		if(this.props.show_title) {
			title = <h4>Device Settings</h4>;
			device_id_row = <div className="row">
        <div className="col s12">
          <span id="device_serial"><strong>Device Serial Number:</strong> {this.props.device_id}</span>
        </div>
      </div>;
		}

    return (
      <section className="device-settings">

			{title}

	<div className="row">
    <form className="col s12" id="device-form">

			{device_id_row}

			<div className="row">
        <div className="input-field col m4 s6">
					<select name="language" id="language" value={this.state.language} onChange={this.onChange} required>
			      <option value="">Choose default device speaking language</option>
      			<option value="en">English</option>
      			<option value="es">Español</option>
      			<option value="ru">Русский</option>
			    </select>
    			<label>Speaking Language</label>
        </div>
      </div>

			<div className="row">
        <div className="input-field col m4 s6">
					<select name="alarm_sound" id="alarm_sound" value={this.state.alarm_sound} onChange={this.onChange} required>
			      <option value="">Choose default alarm sound</option>
      			<option value="voice">Voice</option>
      			<option value="beep">Beep</option>
			    </select>
    			<label>Alarm Sound</label>
        </div>
      </div>

			<div className="row">
        <div className="input-field col m4 s6">
					<select name="alarm_volume" id="alarm_volume" value={this.state.alarm_volume} onChange={this.onChange} required>
			      <option value="">Choose default alarm volume</option>
      			<option value="silent">Silent</option>
      			<option value="quieter">Quieter</option>
      			<option value="normal">Normal</option>
      			<option value="loud">Loud</option>
			    </select>
    			<label>Alarm Volume</label>
        </div>
      </div>

			<div className="row">
        <div className="input-field col m4 s6">
          <input name="alarm_duration" id="alarm_duration" type="number" step="any" className="validate" value={this.state.alarm_duration} onChange={this.onChange} required/>
          <label htmlFor="alarm_duration" className={ (this.state.alarm_duration) ? "active" : null}>Alarm duration (minutes)</label>
        </div>
      </div>

      <div className="row">
			  <button id="patient-submit" className="btn waves-effect waves-light" type="submit" name="action">Submit
    			<i className="material-icons right">assignment_ind</i>
			  </button>
      </div>

    </form>
  </div>
        	
			</section>
    );
  }
});

export default DeviceForm;

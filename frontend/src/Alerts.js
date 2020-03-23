import React from 'react';
import Config from './Config';
import {BatteryUtils} from './Utils';
import pa_logo from './img/pa_logo.png';

var config = new Config();
var $ = window.jQuery = require('jquery');
var moment = require('moment');

/*****
 *
 * Nursing station
 *
 * */

var Alerts = React.createClass({
	getInitialState: function() {

		if(!localStorage['alerts_facility_location_filter']) {
			localStorage.setItem('alerts_facility_location_filter', "all");
		}
		if(!localStorage['alerts_sound_option']) {
			localStorage.setItem('alerts_sound_option', true);
		}
		if(!localStorage['alerts_row_blink']) {
			localStorage.setItem('alerts_row_blink', true);
		}
		if(!localStorage['alerts_page_blink']) {
			localStorage.setItem('alerts_page_blink', true);
		}
		if(!localStorage['alerts_hide_names']) {
			localStorage.setItem('alerts_hide_names', false);
		}

		return {
			state: 'idle',
			pollInterval: "",
			already_buzzed: [],
			facility_location_filter: localStorage['alerts_facility_location_filter'],
			sound_option: localStorage['alerts_sound_option'] === 'true' ? true : false,
			row_blink: localStorage['alerts_row_blink'] === 'true' ? true : false,
			page_blink: localStorage['alerts_page_blink'] === 'true' ? true : false,
			hide_names: localStorage['alerts_hide_names'] === 'true' ? true : false,
		};
	},

	componentDidUpdate: function() {
		$('select').material_select();
	},

	onSubmit: function(event) {
		var self = this;

		var red_alerts = [];
		var yellow_alerts = [];
		var yellow_bordered_alerts = [];
		var purple_alerts = [];
		var orange_alerts = [];
		var orange_bordered_alerts = [];
		var green_alerts = [];
		var sensor_stopped_alerts = [];
		var grey_alerts = [];
		var device_unplugged_alerts = [];
		var facility_locations = {};

		var url = "/api/"+config.APIVersion+"/status-station";
		self.setState({
			state: 'looking up station...',
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
			//data = JSON.parse(data);
			var i = 0;
			var ii = 0;


			for(i=0; i<Object.keys(data.patients).length; i++) {
				var k = Object.keys(data.patients)[i];
				var bli = data.patients[k];
				facility_locations[bli.unit_floor] = 1;
				if(self.state.facility_location_filter != "all" && self.state.facility_location_filter != bli.unit_floor) {
					continue;
				}
				if(!bli.online) {
					var push_event = {};
					push_event.name = bli.name;
					push_event.medical_record_number = bli.medical_record_number;
					push_event.location = "n/a";
					push_event.unit_floor = bli.unit_floor;
					push_event.room = bli.room;
					push_event.since = moment(bli.last_online).format('MMMM Do YYYY, h:mm:ss A');
					grey_alerts.push(push_event);
					//console.log("ADDING GREY");
					//console.log(push_event);

				}
				if(bli.unplugged) {
					var push_event = {};
					push_event.name = bli.name;
					push_event.medical_record_number = bli.medical_record_number;
					push_event.location = "n/a";
					push_event.unit_floor = bli.unit_floor;
					push_event.room = bli.room;
					push_event.since = moment(bli.unplugged_time).format('MMMM Do YYYY, h:mm:ss A');
					device_unplugged_alerts.push(push_event);
				}
				for(ii=0; ii<bli.events.length; ii++) {
					var evtt = bli.events[ii];
					var push_event = {};
					//console.log(bli.events[ii]);
					push_event.medical_record_number = bli.events[ii].medical_record_number;
					push_event.location = bli.events[ii].location.toLowerCase().replace("_"," ");
					var bat = bli.events[ii].battery;
					if(bat) {
						var bp = BatteryUtils.battery_percentage(bat);
						push_event.battery = <span>{bp.text}</span>
					}
					push_event.unit_floor = bli.unit_floor;
					push_event.room = bli.room;
					push_event.name = bli.name;
					push_event.online = bli.online;
					//push_event.since = moment(bli.events[ii].range_start).fromNow();
					push_event.since = moment(bli.events[ii].range_start).format('MMMM Do YYYY, h:mm:ss A');
					//console.log(push_event);
					if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('alarm') > -1)	{
						red_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('falling') > -1) {
						orange_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('recent') > -1) {
						yellow_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('rising') > -1) {
						yellow_bordered_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('recurring') > -1) {
						orange_bordered_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('sensor_stopped') > -1) {
						sensor_stopped_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('24h') > -1) {
						purple_alerts.push(push_event);
					}
					else {
						green_alerts.push(push_event);
					}
				}
			}
			self.setState({
				state: 'idle',

				red_alerts: red_alerts,
				green_alerts: green_alerts,
				orange_alerts: orange_alerts,
				yellow_alerts: yellow_alerts,
				yellow_bordered_alerts: yellow_bordered_alerts,
				orange_bordered_alerts: orange_bordered_alerts,
				purple_alerts: purple_alerts,
				grey_alerts: grey_alerts,
				sensor_stopped_alerts: sensor_stopped_alerts,
				device_unplugged_alerts: device_unplugged_alerts,

				facility_location_select: Object.keys(facility_locations).map(function(val, index) {
					return(<option key={"location_filter_"+val} value={val}>{val}</option>);
				}),

				red_alerts_jsx: Object.keys(red_alerts).map(function(val, index){
					var short_mrn = "";
					if (red_alerts[val].medical_record_number){
						short_mrn = red_alerts[val].medical_record_number.toString();
						short_mrn = short_mrn.substr(short_mrn.length - 5).replace(" ", "-");
					}
					else if (!red_alerts[val].medical_record_number){
						short_mrn = red_alerts[val].name.toLowerCase().substr(red_alerts[val].name.length - 5).replace(" ", "-");
					}
					var name_or_id = "";
					if (self.state.hide_names){
						name_or_id = short_mrn;
					}
					else {
						name_or_id = red_alerts[val].name;
					}
					return (<tr key={red_alerts[val].medical_record_number+"|"+red_alerts[val].location} className="red">
						<td className="alert_names_column">{red_alerts[val].name}</td>
						<td className="alert_identifiers_column">{short_mrn}</td>
						<td>{red_alerts[val].location}</td>
						<td>{red_alerts[val].battery}</td>
						<td>{red_alerts[val].unit_floor}</td>
						<td>{red_alerts[val].room}</td>
						<td>Alarm!</td>
						<td>{red_alerts[val].since}</td>
					</tr>);
				}),
				yellow_alerts_jsx: Object.keys(yellow_alerts).map(function(val, index){
					var short_mrn = "";
					if (yellow_alerts[val].medical_record_number){
						short_mrn = yellow_alerts[val].medical_record_number.toString();
						short_mrn = short_mrn.substr(short_mrn.length - 5).replace(" ", "-");
					}
					else if (!yellow_alerts[val].medical_record_number){
						short_mrn = yellow_alerts[val].name.toLowerCase().substr(yellow_alerts[val].name.length - 5).replace(" ", "-")
					}
					return (<tr key={yellow_alerts[val].medical_record_number+"|"+yellow_alerts[val].location} className="yellow">
						<td className="alert_names_column">{yellow_alerts[val].name}</td>
						<td className="alert_identifiers_column">{short_mrn}</td>
						<td>{yellow_alerts[val].location}</td>
						<td>{yellow_alerts[val].battery}</td>
						<td>{yellow_alerts[val].unit_floor}</td>
						<td>{yellow_alerts[val].room}</td>
						<td>Recent pressure</td>
						<td>{yellow_alerts[val].since}</td>
					</tr>);
				}),
				yellow_bordered_alerts_jsx: Object.keys(yellow_bordered_alerts).map(function(val, index){
					var short_mrn = "";
					if (yellow_bordered_alerts[val].medical_record_number){
						short_mrn = yellow_bordered_alerts[val].medical_record_number.toString();
						short_mrn = short_mrn.substr(short_mrn.length - 5).replace(" ", "-");
					}
					else if (!yellow_bordered_alerts[val].medical_record_number){
						short_mrn = yellow_bordered_alerts[val].name.toLowerCase().substr(yellow_bordered_alerts[val].name.length - 5).replace(" ", "-")
					}
					return (<tr key={yellow_bordered_alerts[val].medical_record_number+"|"+yellow_bordered_alerts[val].location} className="bordered-yellow">
						<td className="alert_names_column">{yellow_bordered_alerts[val].name}</td>
						<td className="alert_identifiers_column">{short_mrn}</td>
						<td>{yellow_bordered_alerts[val].location}</td>
						<td>{yellow_bordered_alerts[val].battery}</td>
						<td>{yellow_bordered_alerts[val].unit_floor}</td>
						<td>{yellow_bordered_alerts[val].room}</td>
						<td>Pressure rising</td>
						<td>{yellow_bordered_alerts[val].since}</td>
					</tr>);
				}),
				orange_alerts_jsx: Object.keys(orange_alerts).map(function(val, index){
					var short_mrn = "";
					if (orange_alerts[val].medical_record_number){
						short_mrn = orange_alerts[val].medical_record_number.toString();
						short_mrn = short_mrn.substr(short_mrn.length - 5).replace(" ", "-");
					}
					else if (!orange_alerts[val].medical_record_number){
						short_mrn = orange_alerts[val].name.toLowerCase().substr(orange_alerts[val].name.length - 5).replace(" ", "-")
					}
					return (<tr key={orange_alerts[val].medical_record_number+"|"+orange_alerts[val].location} className="orange">
						<td className="alert_names_column">{orange_alerts[val].name}</td>
						<td className="alert_identifiers_column">{short_mrn}</td>
						<td>{orange_alerts[val].location}</td>
						<td>{orange_alerts[val].battery}</td>
						<td>{orange_alerts[val].unit_floor}</td>
						<td>{orange_alerts[val].room}</td>
						<td>Pressure falling</td>
						<td>{orange_alerts[val].since}</td>
					</tr>);
				}),
				orange_bordered_alerts_jsx: Object.keys(orange_bordered_alerts).map(function(val, index){
					var short_mrn = "";
					if (orange_bordered_alerts[val].medical_record_number){
						short_mrn = orange_bordered_alerts[val].medical_record_number.toString();
						short_mrn = short_mrn.substr(short_mrn.length - 5).replace(" ", "-");
					}
					else if (!orange_bordered_alerts[val].medical_record_number){
						short_mrn = orange_bordered_alerts[val].name.toLowerCase().substr(orange_bordered_alerts[val].name.length - 5).replace(" ", "-")
					}
					return (<tr key={orange_bordered_alerts[val].medical_record_number+"|"+orange_bordered_alerts[val].location} className="bordered-orange">
						<td className="alert_names_column">{orange_bordered_alerts[val].name}</td>
						<td className="alert_identifiers_column">{short_mrn}</td>
						<td>{orange_bordered_alerts[val].location}</td>
						<td>{orange_bordered_alerts[val].battery}</td>
						<td>{orange_bordered_alerts[val].unit_floor}</td>
						<td>{orange_bordered_alerts[val].room}</td>
						<td>Pressure reccuring</td>
						<td>{orange_bordered_alerts[val].since}</td>
					</tr>);
				}),
				green_alerts_jsx: Object.keys(green_alerts).map(function(val, index){
					var short_mrn = "";
					if (green_alerts[val].medical_record_number){
						short_mrn = green_alerts[val].medical_record_number.toString();
						short_mrn = short_mrn.substr(short_mrn.length - 5).replace(" ", "-");
					}
					else if (!green_alerts[val].medical_record_number){
						short_mrn = green_alerts[val].name.toLowerCase().substr(green_alerts[val].name.length - 5).replace(" ", "-");
					}
					return (<tr key={green_alerts[val].medical_record_number+"|"+green_alerts[val].location} className="green">
						<td className="alert_names_column">{green_alerts[val].name}</td>
						<td className="alert_identifiers_column">{short_mrn}</td>
						<td>{green_alerts[val].location}</td>
						<td>{green_alerts[val].battery}</td>
						<td>{green_alerts[val].unit_floor}</td>
						<td>{green_alerts[val].room}</td>
						<td>No pressure</td>
						<td>{green_alerts[val].since}</td>
					</tr>);
				}),
				purple_alerts_jsx: Object.keys(purple_alerts).map(function(val, index){
					var short_mrn = "";
					if (purple_alerts[val].medical_record_number){
						short_mrn = purple_alerts[val].medical_record_number.toString();
						short_mrn = short_mrn.substr(short_mrn.length - 5).replace(" ", "-");
					}
					else if (!purple_alerts[val].medical_record_number){
						short_mrn = purple_alerts[val].name.toLowerCase().substr(purple_alerts[val].name.length - 5).replace(" ", "-");
					}
					return (<tr key={purple_alerts[val].medical_record_number+"|"+purple_alerts[val].location} className="purple lighten-2">
						<td className="alert_names_column">{purple_alerts[val].name}</td>
						<td className="alert_identifiers_column">{short_mrn}</td>
						<td>{purple_alerts[val].location}</td>
						<td>{purple_alerts[val].battery}</td>
						<td>{purple_alerts[val].unit_floor}</td>
						<td>{purple_alerts[val].room}</td>
						<td>Sensor inactive for 24 hours</td>
						<td>{purple_alerts[val].since}</td>
					</tr>);
				}),
				sensor_stopped_alerts_jsx: Object.keys(sensor_stopped_alerts).map(function(val, index){
					var short_mrn = "";
					if (sensor_stopped_alerts[val].medical_record_number){
						short_mrn = sensor_stopped_alerts[val].medical_record_number.toString();
						short_mrn = short_mrn.substr(short_mrn.length - 5).replace(" ", "-");
					}
					else if (!sensor_stopped_alerts[val].medical_record_number){
						short_mrn = sensor_stopped_alerts[val].name.toLowerCase().substr(sensor_stopped_alerts[val].name.length - 5).replace(" ", "-");
					}
					return (<tr key={sensor_stopped_alerts[val].medical_record_number+"|"+sensor_stopped_alerts[val].location} className="grey darken-2">
						<td className="alert_names_column">{sensor_stopped_alerts[val].name}</td>
						<td className="alert_identifiers_column">{short_mrn}</td>
						<td>{sensor_stopped_alerts[val].location}</td>
						<td>N/A</td>
						<td>{sensor_stopped_alerts[val].unit_floor}</td>
						<td>{sensor_stopped_alerts[val].room}</td>
						<td>Sensor Stopped</td>
						<td>{sensor_stopped_alerts[val].since}</td>
					</tr>);
				}),
				device_unplugged_alerts_jsx: Object.keys(device_unplugged_alerts).map(function(val, index){
					var short_mrn = "";
					if (device_unplugged_alerts[val].medical_record_number){
						short_mrn = device_unplugged_alerts[val].medical_record_number.toString();
						short_mrn = short_mrn.substr(short_mrn.length - 5).replace(" ", "-");
					}
					else if (!device_unplugged_alerts[val].medical_record_number){
						short_mrn = device_unplugged_alerts[val].name.toLowerCase().substr(device_unplugged_alerts[val].name.length - 5).replace(" ", "-")
					}
					return (<tr key={device_unplugged_alerts[val].medical_record_number+"|"+device_unplugged_alerts[val].name} className="grey darken-1">
						<td className="alert_names_column">{device_unplugged_alerts[val].name}</td>
						<td className="alert_identifiers_column">{short_mrn}</td>
						<td>{device_unplugged_alerts[val].location}</td>
						<td>N/A</td>
						<td>{device_unplugged_alerts[val].unit_floor}</td>
						<td>{device_unplugged_alerts[val].room}</td>
						<td>Device Unplugged</td>
						<td>{device_unplugged_alerts[val].since}</td>
					</tr>);
				}),
				grey_alerts_jsx: Object.keys(grey_alerts).map(function(val, index){
					var short_mrn = "";
					if (grey_alerts[val].medical_record_number){
						short_mrn = grey_alerts[val].medical_record_number.toString();
						short_mrn = short_mrn.substr(short_mrn.length - 5).replace(" ", "-");
					}
					else if (!grey_alerts[val].medical_record_number){
						short_mrn = grey_alerts[val].name.toLowerCase().substr(grey_alerts[val].name.length - 5).replace(" ", "-");
					}
					return (<tr key={grey_alerts[val].medical_record_number+"|"+grey_alerts[val].name} className="grey">
						<td className="alert_names_column">{grey_alerts[val].name}</td>
						<td className="alert_identifiers_column">{short_mrn}</td>
						<td>{grey_alerts[val].location}</td>
						<td>N/A</td>
						<td>{grey_alerts[val].unit_floor}</td>
						<td>{grey_alerts[val].room}</td>
						<td>Offline</td>
						<td>{grey_alerts[val].since}</td>
					</tr>);
				})
			});

			var reds = red_alerts;
			var bzd = self.state.already_buzzed;
			var bzd_new = []
			Object.keys(reds).map(function(val, index) {
				var bid = reds[val].medical_record_number + "_"+reds[val].location.toLowerCase()
				if(bzd.indexOf(bid) > -1) {
					//TODO: add a timestamp here so can expire them on some frequency.
					//TODO: add another interval function somewhere to remove expired ones so they can buzz again
					bzd_new.push(bid);
				}
				else {
					//not in there
					bzd_new.push(bid);
					//play sound and alert, only if sound enabled
					if(self.state.sound_option) {
						$("#play-alarm").trigger("click");
						self.blinkAlerts();
					}
				}
			});
			self.setState({
				already_buzzed: bzd_new,
			});
		});

	},

	blinkAlerts: function() {
		if(this.state.row_blink) {
			$('#alerts-table > tbody > tr:first').delay(300)
				.qclass('red')
				.delay(300)
				.qclass('purple')
				.delay(300)
				.qclass('red')
				.delay(300)
				.qclass('purple')
				.delay(300)
				.qclass('red')
				.delay(300)
				.qclass('purple')
				.delay(300)
				.qclass('red')
				.delay(300)
				.qclass('purple')
				.delay(300)
				.qclass('red')
				.delay(300)
				.qclass('purple')
				.delay(300)
				.qclass('red')
				.delay(300)
				.qclass('purple')
				.delay(300)
				.qclass('red');
		}
		if(this.state.page_blink) {
			$("#root").delay(300)
				.qclass('alerts_page_blink_white')
				.delay(300)
				.qclass('alerts_page_blink_red')
				.delay(300)
				.qclass('alerts_page_blink_white')
				.delay(300)
				.qclass('alerts_page_blink_red')
				.delay(300)
				.qclass('alerts_page_blink_white')
				.delay(300)
				.qclass('alerts_page_blink_red')
				.delay(300)
				.qclass('alerts_page_blink_white')
				.delay(300)
				.qclass('alerts_page_blink_red')
				.delay(300)
				.qclass('alerts_page_blink_white')
				.delay(300)
				.qclass('alerts_page_blink_red')
				.delay(300)
				.qclass('alerts_page_blink_white')
				.delay(300)
				.qclass('alerts_page_blink_red')
				.delay(300)
				.qclass('alerts_page_blink_white');
		}
	},

	componentDidMount: function() {
		this.onSubmit();
		var flash_delay;
		var self = this;
		var buzzer = document.getElementById("alarm-sound");
		$("#play-alarm").on('click', function() {
			buzzer.currentTime = 0;
			buzzer.play();
			setTimeout(function() {
				buzzer.pause();
				buzzer.currentTime = 0;
			}, 4000);
		});

		//set to refresh
		var poll_interval = setInterval(this.onSubmit, 5000);
		this.state.pollInterval = poll_interval;
		$('select').material_select();
		$('select').on('change', this.onChange);
		// for HTML5 "required" attribute
		$("select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
	},

	onChange: function(e, ee) {
		var x = $(e.target).attr('id');
		if($(e.target).is(':checkbox')) {
			this.state[x] = $(e.target).prop("checked");
		}
		else {
			this.state[x] = e.target.value;
			$('select').material_select();
			this.onSubmit();
		}

		localStorage.setItem('alerts_'+x, this.state[x]);
		this.setState(this.state);
	},

	componentWillUnmount: function() {
		clearInterval(this.state.pollInterval);
	},

	render: function() {

		if (this.state.hide_names){
			$('.alert_names_column').attr("hidden", true);
			$('.alert_identifiers_column').attr("hidden", false);
		}
		else {
			$('.alert_names_column').attr("hidden", false);
			$('.alert_identifiers_column').attr("hidden", true);
		}
	  return (
			<section className="a-table">
				<audio src={"/sounds/chime.mp3"} type="audio/mpeg" id="alarm-sound"/>
				<div className="top-right-button hide">
					<a className="btn-floating btn-large waves-effect waves-light red" id="play-alarm"><i className="material-icons">add</i></a>
					<span>BZZZ</span>
				</div>
				<div className="right">
					<p>
						<input type="checkbox" id="sound_option" onChange={this.onChange} checked={this.state.sound_option}/>
						<label htmlFor="sound_option">Play sound for alarms</label>
					</p>
					<p>
						<input type="checkbox" id="row_blink" onChange={this.onChange} checked={this.state.row_blink}/>
						<label htmlFor="row_blink">Flash row for alarms</label>
					</p>
					<p>
						<input type="checkbox" id="page_blink" onChange={this.onChange} checked={this.state.page_blink}/>
						<label htmlFor="page_blink">Flash page for alarms</label>
					</p>
					<p>
						<input type="checkbox" id="hide_names" onChange={this.onChange} checked={this.state.hide_names}/>
						<label htmlFor="hide_names">Hide Patient Names</label>
					</p>
				</div>

				<form>
					<div className="row">
						<div className="input-field col s3">
							<select name="facility_location_filter" id="facility_location_filter" onChange={this.onChange} value={this.state.facility_location_filter}>
								<option value="all">All</option>
								{this.state.facility_location_select}
							</select>
							<label>Facility Location To Show</label>
						</div>
					</div>
				</form>

				<table id="alerts-table">
					<thead>
						<tr>
							<th data-field="medical_record_number" className="alert_names_column">Patient Name or Identifier</th>
							<th data-field="medical_record_number" className="alert_identifiers_column">Patient ID</th>
							<th data-field="body_location">Body Location</th>
							<th data-field="sensor_battery">Sensor Battery</th>
							<th data-field="hospital_location">Facility Location</th>
							<th data-field="room">Room</th>
							<th data-field="alert_level">Alert Level</th>
							<th data-field="since">Since</th>
						</tr>
					</thead>
					<tbody>
						{this.state.red_alerts_jsx}
						{this.state.grey_alerts_jsx}
						{this.state.device_unplugged_alerts_jsx}
						{this.state.sensor_stopped_alerts_jsx}
						{this.state.orange_bordered_alerts_jsx}
						{this.state.orange_alerts_jsx}
						{this.state.yellow_bordered_alerts_jsx}
						{this.state.yellow_alerts_jsx}
						{this.state.green_alerts_jsx}
						{this.state.purple_alerts_jsx}
					</tbody>
				</table>
			</section>
		);
	}
});

var DashboardAlerts = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
			pollInterval: "",
			facility_location_filter: "all",
			red_alerts : [],
			yellow_alerts : [],
			yellow_bordered_alerts : [],
			orange_alerts : [],
			orange_bordered_alerts : [],
			green_alerts : [],
			sensor_stopped_alerts : [],
			grey_alerts : [],
			device_unplugged_alerts: [],
			purple_alerts: [],
		};
	},

	componentDidUpdate: function() {
		$('select').material_select();
		$('.tooltipped').tooltip('remove');
		$('.tooltipped').tooltip({delay: 50});
	},

	onSubmit: function(event) {
		var self = this;

		var red_alerts = [];
		var yellow_alerts = [];
		var yellow_bordered_alerts = [];
		var orange_alerts = [];
		var orange_bordered_alerts = [];
		var green_alerts = [];
		var sensor_stopped_alerts = [];
		var purple_alerts = [];
		var grey_alerts = [];
		var device_unplugged_alerts = [];
		var facility_locations = {};

		var url = "/api/"+config.APIVersion+"/status-station";
		self.setState({
			state: 'looking up station...',
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
			//data = JSON.parse(data);

			var i = 0;
			var ii = 0;


			for(i=0; i<Object.keys(data.patients).length; i++) {
				var k = Object.keys(data.patients)[i];
				var bli = data.patients[k];
				facility_locations[bli.unit_floor] = 1;
				if(self.state.facility_location_filter != "all" && self.state.facility_location_filter != bli.unit_floor) {
					continue;
				}
				if(!bli.online) {
					var push_event = {};
					push_event.name = bli.name;
					push_event.location = "n/a";
					push_event.unit_floor = bli.unit_floor;
					push_event.room = bli.room;
					push_event.since = moment(bli.last_online).format('MMMM Do YYYY, h:mm:ss A');
					grey_alerts.push(push_event);
					//console.log("ADDING GREY");
					//console.log(push_event);

				}
				if(bli.unplugged) {
					var push_event = {};
					push_event.name = bli.name;
					push_event.location = "n/a";
					push_event.unit_floor = bli.unit_floor;
					push_event.room = bli.room;
					push_event.since = moment(bli.unplugged_time).format('MMMM Do YYYY, h:mm:ss A');
					device_unplugged_alerts.push(push_event);
				}
				for(ii=0; ii<bli.events.length; ii++) {
					var evtt = bli.events[ii];
					var push_event = {};
					//console.log(bli.events[ii]);
					push_event.medical_record_number = bli.events[ii].medical_record_number;
					push_event.location = bli.events[ii].location.toLowerCase().replace("_"," ");
					push_event.unit_floor = bli.unit_floor;
					push_event.room = bli.room;
					push_event.name = bli.name;
					push_event.online = bli.online;
					//push_event.since = moment(bli.events[ii].range_start).fromNow();
					push_event.since = moment(bli.events[ii].range_start).format('MMMM Do YYYY, h:mm:ss A');
					//console.log(push_event);
					if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('alarm') > -1)	{
						red_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('falling') > -1) {
						orange_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('recent') > -1) {
						yellow_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('rising') > -1) {
						yellow_bordered_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('recurring') > -1) {
						orange_bordered_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('sensor_stopped') > -1) {
						sensor_stopped_alerts.push(push_event);
					}
					else if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('24h') > -1) {
						purple_alerts.push(push_event);
					}
					else {
						green_alerts.push(push_event);
					}
				}
			}
			self.setState({
				state: 'idle',

				red_alerts: red_alerts,
				green_alerts: green_alerts,
				orange_alerts: orange_alerts,
				yellow_alerts: yellow_alerts,
				yellow_bordered_alerts: yellow_bordered_alerts,
				orange_bordered_alerts: orange_bordered_alerts,
				grey_alerts: grey_alerts,
				purple_alerts: purple_alerts,
				sensor_stopped_alerts: sensor_stopped_alerts,
				device_unplugged_alerts: device_unplugged_alerts,
			});

		});
	},

	componentDidMount: function() {
		this.onSubmit();
		var flash_delay;
		var self = this;

		//set to refresh
		var poll_interval = setInterval(this.onSubmit, 15000);
		this.state.pollInterval = poll_interval;
		$('select').material_select();
		$('select').on('change', this.onChange);
		// for HTML5 "required" attribute
		$("select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
		$('.tooltipped').tooltip({delay: 50});
	},

	onChange: function(e, ee) {
		var x = $(e.target).attr('id');
		if($(e.target).is(':checkbox')) {
			this.state[x] = $(e.target).prop("checked");
		}
		else {
			this.state[x] = e.target.value;
			$('select').material_select();
			this.onSubmit();
		}
		this.setState(this.state);
	},

	componentWillUnmount: function() {
		clearInterval(this.state.pollInterval);
		$('.tooltipped').tooltip('remove');
	},

	render: function() {
		return (
			<div>
				<div className="card dashboard-card" style={{'minHeight': 200 + 'px', height: 'auto'}}>
					<div className="card-content" style={{'minHeight': 164 + 'px', height: 'auto'}}>
						<div className="card-title">Alerts</div>
						<div className="chip red tooltipped rounded" data-position="top" data-delay="50" data-tooltip={this.state.red_alerts.length+" alarm events"}>
							{this.state.red_alerts.length}
						</div>
						<div className="chip grey tooltipped rounded" data-position="top" data-delay="50" data-tooltip={this.state.grey_alerts.length+" offline tablets"}>
							{this.state.grey_alerts.length}
						</div>
						<div className="chip grey lighten-1 tooltipped rounded" data-position="top" data-delay="50" data-tooltip={this.state.device_unplugged_alerts.length+" uplugged tablets"}>
							{this.state.device_unplugged_alerts.length}
						</div>
						<div className="chip purple lighten-2 tooltipped rounded" data-position="top" data-delay="50" data-tooltip={this.state.purple_alerts.length+" inactive sensors"}>
							{this.state.purple_alerts.length}
						</div>
						<div className="chip grey darken-1 tooltipped rounded" data-position="top" data-delay="50" data-tooltip={this.state.sensor_stopped_alerts.length+" offline sensors"}>
							{this.state.sensor_stopped_alerts.length}
						</div>
						<div className="chip orange tooltipped rounded" data-position="top" data-delay="50" data-tooltip={this.state.orange_alerts.length+" decreasing pressure events"}>
							{this.state.orange_alerts.length}
						</div>
						<div className="chip bordered-orange tooltipped rounded" data-position="top" data-delay="50" data-tooltip={this.state.orange_bordered_alerts.length+" recurring pressure events"}>
							{this.state.orange_bordered_alerts.length}
						</div>
						<div className="chip yellow tooltipped rounded" data-position="top" data-delay="50" data-tooltip={this.state.yellow_alerts.length+" recent pressure events"}>
							{this.state.yellow_alerts.length}
						</div>
						<div className="chip bordered-yellow tooltipped rounded" data-position="top" data-delay="50" data-tooltip={this.state.yellow_bordered_alerts.length+" increasing pressure events"}>
							{this.state.yellow_bordered_alerts.length}
						</div>
						<div className="chip green tooltipped rounded" data-position="top" data-delay="50" data-tooltip={this.state.green_alerts.length+" off pressure events"}>
							{this.state.green_alerts.length}
						</div>
					</div>
					<div className="card-action">
						<a href={config.baseUrl+"/alerts"}>View Alerts</a>
					</div>
				</div>
			</div>
		);
	}
});

export {Alerts, DashboardAlerts};

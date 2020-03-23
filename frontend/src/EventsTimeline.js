import React from 'react';
import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');
var vis = require('vis');

/*****
 *
 * Events Timeline for a patient
 * 
 * */

var EventsTimeline = React.createClass({

	getInitialState: function() {
		return {
			state: '',
			devices: <div>No alerts</div>
		};
	},

	onSubmit: function(event) {
		//event.preventDefault();
		var self = this;
		//var url = "https://dm.nemik.net/ui/xajax/events";
		var url = "/api/"+config.APIVersion+"/timelines?medical_record_number="+this.props.medical_record_number;
		self.setState({
			state: 'Looking up events...',
		});
		$.ajax(
			{
				url: url,
				beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}).done(function(data){
				//console.log("tl data "+JSON.stringify(data));
				self.setState({
					state: 'done',
					events: data,
					patient_name: data.name,
				});
			}).fail(function (data) {
				self.setState({
					state: 'No events',
					events: [],
					patient_name: data.name,
				});
        	});
	},

	componentDidMount: function() {
		this.onSubmit();
		//do this again in 10 seconds
		//setInterval(this.onSubmit, 10000);
	},

	componentDidUpdate: function(prevProps, prevState){
		if(this.state.state != 'done') {
			return;
		}

		//var events = JSON.parse(this.state.events);
		var events = this.state.events.events;

		var gs = new Array;
		var eitems = new Array;
		var it = 0;
		gs.push({id: "general", content: "General", value: -1});
		for(var i=0; i< events.length; i++) {
			//console.log(events[i].message);
			if(events[i].instance && events[i].instance != "")
			{
				var t_start = new Date(events[i].instance);
				eitems.push({className: "blue", id: it, group: "general", content: events[i].message, start: new Date(t_start)});
				//console.log("eitems : "+JSON.stringify(eitems));
				it = it+1;
			}
			else 
			{
				var group_exists = false;
				for(var j=0; j<gs.length; j++)
				{
					if(gs[j].id==events[i].location)
					{
						group_exists = true;
					}
				}
				if(!group_exists) {
					gs.push({id: events[i].location, content: events[i].location.replace("_"," ").toLowerCase(), value: i});
				}
				var color = "green";
				var text = "";
				switch(events[i].message) {
					case "PRESSURE_ALARM":{
						color = "red";
						text = "Alarm";
						break;
					}
					case "PRESSURE_RISING":{
						color = "bordered-yellow";
						text = "Pressure rising";
						break;
					}
					case "PRESSURE_FALLING":{
						color="orange";
						text = "Pressure falling";
						break;
					}
					case "RECENT_PRESSURE":{
						color= "yellow";
						text = "Recent pressure";
						break;
					}
					case "PRESSURE_RECURRING":{
						color= "bordered-orange";
						text = "Pressure recurring after alarm";
						break;
					}
					case "INACTIVE_FOR_24H":{
						color= "purple lighten-2";
						text = "Sensor inactive";
						break;
					}
					case "NO_PRESSURE":
					default: {
						text = "No pressure";
						color = "green";
					}
				}
				var dd = new Date(0);
				var ddd = new Date(0);
				var t_start = new Date(events[i].range_start);
				var t_end = new Date();
				if(events[i].range_end && events[i].range_end != "")
				{
					t_end = new Date(events[i].range_end);
				}
				eitems.push({className: color, id: it, group: events[i].location, content: text, start: new Date(t_start), end: new Date(t_end)});
				//console.log("eitems : "+JSON.stringify(eitems));
				it = it+1;
			}
		}

		var groups = new vis.DataSet(
			gs
		);

		// create a dataset with items
		// note that months are zero-based in the JavaScript Date object, so month 3 is April
		var items = new vis.DataSet(
			eitems
			/*
		[
		{id: 0, group: 0, content: 'item 0', start: new Date(2014, 3, 17), end: new Date(2014, 3, 21)},
		{id: 1, group: 0, content: 'item 1', start: new Date(2014, 3, 19), end: new Date(2014, 3, 20)},
		{id: 2, group: 1, content: 'item 2', start: new Date(2014, 3, 16), end: new Date(2014, 3, 24)},
		{id: 3, group: 1, content: 'item 3', start: new Date(2014, 3, 23), end: new Date(2014, 3, 24)},
		{id: 4, group: 1, content: 'item 4', start: new Date(2014, 3, 22), end: new Date(2014, 3, 26)},
		{id: 5, group: 2, content: 'item 5', start: new Date(2014, 3, 24), end: new Date(2014, 3, 27)}
		]
		*/
		);

		// create visualization
		var container = document.getElementById('visualization');
		$(container).empty();
		var timeline = new vis.Timeline(container);
		var ago = new Date();
		ago.setDate(ago.getDate() - 3);
		var options = {
			// option groupOrder can be a property name or a sort function
			// the sort function must compare two groups and return a value
			//     > 0 when a > b
			//     < 0 when a < b
			//       0 when a == b
			groupOrder: function (a, b) {
				return a.value - b.value;
			},
			editable: false,
			showCurrentTime: false,
			align: 'right',
			start: ago,
			end: new Date(),
		};

		timeline.setOptions(options);
		timeline.setGroups(groups);
		timeline.setItems(items);

		var zoom = function (percentage) {
			var range = timeline.getWindow();
			var interval = range.end - range.start;

			timeline.setWindow({
				start: range.start.valueOf() - interval * percentage,
				end:   range.end.valueOf()   + interval * percentage
			});
		};

		document.getElementById('zoom_in').onclick  = function () { zoom(-0.2); };
		document.getElementById('zoom_out').onclick  = function () { zoom(0.2); };

	},

	render: function() {

		if(this.state.state != 'done') {
			return <div>{this.state.state}</div>
		}
		return (
			<div>
				<h5 className="left-align chart_patient_name">{this.state.patient_name}</h5>
				<div id="visualization"></div>
				<div className="right chart_zoom_controls">
					<a><i className="material-icons" id="zoom_in">zoom_in</i></a>
					<a><i className="material-icons" id="zoom_out">zoom_out</i></a>
				</div>
			</div>
		)
	}
});

export default EventsTimeline;

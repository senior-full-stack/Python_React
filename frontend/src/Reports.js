import React from 'react';
import Config from './Config';
import { BatteryUtils, DateUtils } from './Utils';
import Select from 'react-select';
import 'react-select/dist/react-select.css';

import excel_icon from './img/excel_icon.png';

var config = new Config();
var $ = window.jQuery = require('jquery');
var moment = require('moment');
var marked = require('marked');
var MAX_REPORT_ENTRIES = 1000;

//var handsontable = require('handsontable');
import Handsontable from './../node_modules/handsontable/dist/handsontable.full';

var ReportsNav = React.createClass({
	selectedPatients: [{value: "", label: "All Patients"}],
	getInitialState: function() {
		//get them from sessionstorage
		var start = '2010-01-01';
		var end = moment().format('YYYY-MM-DD');
		var unit = "All Units";
		var patient = "All Patients";
		var patient_mrn = "";

		if(sessionStorage['report_start']) {
			start = sessionStorage['report_start'];
		}
		else {
			sessionStorage['report_start'] = start;
			sessionStorage['utc_report_start'] = DateUtils.to_utc_date(start);
		}

		if(sessionStorage['report_end']) {
			end = sessionStorage['report_end'];
		}
		else {
			sessionStorage['report_end'] = end;
			sessionStorage['utc_report_end'] = DateUtils.to_utc_date(end);
		}

		if(sessionStorage['unit']) {
			unit = sessionStorage['unit'];
		}
		else {
			sessionStorage['unit'] = unit;
		}

		if(sessionStorage['patient']) {
			patient = sessionStorage['patient'];
		}
		else {
			sessionStorage['patient'] = patient;
		}

		if(sessionStorage['patient_mrn']) {
			patient_mrn = sessionStorage['patient_mrn'];
		}

		var active_report = this.props.active_member;
		var report = "Patient Info";
		var href = "/reports/info";

		if(this.props.active_member === "pu"){
			report = "PU Status";
			href = "/reports/pu";
		}
		else if(this.props.active_member === "events"){
			report = "Events";
			href = "/reports/events";
		}
		else if(this.props.active_member === "repositions"){
			report = "Reposition";
			href = "/reports/reposition";
		}
		else if(this.props.active_member === "alarmresponses"){
			report = "Alarm Response";
			href = "/reports/alarm_response";
		}

		sessionStorage['report_href'] = href;
		sessionStorage['active_report'] = active_report;
		sessionStorage['report_view'] = report;

		return {
			report_view: report,
			report_href: href,
			report_active_member: active_report,
			report_start: start,
			report_end: end,
			report_unit: unit,
			report_patient: patient,
			report_mrn: patient_mrn,
			available_unit_floors: [],
			patient_list: [],
			parameters_label: "",
		};
	},

	getUnitFloors: function() {
		var self = this;
		var url = "/api/"+config.APIVersion+"/admin";
		$.ajax(
			{
				url: url,
				type: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
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

	getPatientsList: function() {
		var self = this;
		var url = "/api/"+config.APIVersion+"/patients";
		self.setState({
			state: 'looking up patients...',
		});
		$.ajax(
			{
				url: url,
				method: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}
		).done(function(data) {
				self.setState({
					patient_list: [{value: "", label: "All Patients", unit_floor: "" }].concat(data.patients.map((patient) => {
						return {
							label: patient.name + ' ' + patient.last_name,
							value: patient.medical_record_number,
							unit_floor: patient.unit_floor
						}
					}))
				});
			});
	},

	componentDidMount: function() {
		$('select').material_select();
		$('select').on('change', this.onSelectionChange);
		this.getUnitFloors();
		this.getPatientsList();
		this.setParametersLabel();
		$.setup_pickadate(this);
	},

	componentDidUpdate: function() {
		$('select').material_select();
	},
	onPatientSelectionChange: function(val) {
		console.log(val);
		let target = $('#report_patient');
		target.value = val;
		if (val.filter(e => e.value === "").length > 0 && this.selectedPatients.filter(e => e.value === "").length === 0 || val.length === 0) {
			val = [{value: "", label: "All Patients", unit_floor: ""}]
		}
		else if (val.filter(e => e.value === "").length > 0 && this.selectedPatients.filter(e => e.value === "").length > 0 && val.length > 1) {
			val = val.filter(e => e.value !== "");
		}
		this.selectedPatients = val;
		console.log(this.selectedPatients );
		this.onSelectionChange({target: target});
	},
	onSelectionChange: function(e, ee) {
		var patient_mrn = this.selectedPatients.map((patient) => patient.value);
		var selected_report_href = $('#report_view option:selected').attr('data-report_href');
		var selected_active_report = $('#report_view option:selected').attr('data-active_report');
		var selection = $(e.target).attr('id');
		this.state[selection] = e.target.value;
		var selected_option = this.state[selection];
		if(selection === "report_patient") {
			selected_option = this.selectedPatients.map((patient) => patient.label);
			if(selected_option === "All Patients") {
				patient_mrn = "";
			}
			this.setState({
				report_patient: selected_option,
				report_mrn: patient_mrn,
			});
		}
		if(selection === "report_unit" && selected_option !== sessionStorage['unit']) {
			this.setState({
				report_patient: "All Patients",
				report_unit: selected_option,
				report_mrn: "",
			});
		}
		if(selection === "report_view") {
			this.setState({
				report_view: selected_option,
				report_href: selected_report_href,
				report_active_member: selected_active_report,
			});
		}
	},

	onFilterClick: function() {
		sessionStorage['report_start'] = this.state.report_start;
		sessionStorage['report_end'] = this.state.report_end;
		sessionStorage['utc_report_start'] = DateUtils.to_utc_date(this.state.report_start);
		sessionStorage['utc_report_end'] = DateUtils.to_utc_date(this.state.report_end);
		sessionStorage['patient'] = this.state.report_patient;
		sessionStorage['patient_mrn'] = this.state.report_mrn;
		sessionStorage['unit'] = this.state.report_unit;
		sessionStorage['report_view'] = this.state.report_view;
		sessionStorage['active_report'] = this.state.report_active_member;
		sessionStorage['report_href'] = this.state.report_href;

		this.setParametersLabel();
		window.dispatchEvent(new Event('filterChange'));
	},

	setParametersLabel() {
		var param_label = <div className="right-align"><span className="grey-text" style={{fontSize:80+"%"}}>
			Report: <i className="teal-text">{sessionStorage['report_view']}</i>,
			Unit: <i className="teal-text">{sessionStorage['unit']}</i>,
			Patients: <i className="teal-text">{sessionStorage['patient']}</i>,
			Range: <i className="teal-text">{sessionStorage['report_start']}</i> - <i className="teal-text">{sessionStorage['report_end']}</i>
		</span></div>;
		if(this.props.medical_record_number) {
			param_label = <div className="right-align"><span className="grey-text" style={{fontSize:80+"%"}}>
				Report: <i className="teal-text">{sessionStorage['report_view']}</i>,
				Range: <i className="teal-text">{sessionStorage['report_start']}</i> - <i className="teal-text">{sessionStorage['report_end']}</i>
			</span></div>;
		}

		this.setState({
			parameters_label: param_label
		})
	},

	render: function() {
		var self = this;
		var info_href = "/reports/info";
		var pu_href = "/reports/pu";
		var events_href = "/reports/events";
		var reposition_href = "/reports/reposition";
		var alarm_response_href = "/reports/alarm_response";
		var hide_list = "";
		var cannot_filter = "";
		var date_message = "";
		var hide_button = "";
		var offset_date = "";
		if(this.props.medical_record_number) {
			info_href = "/patient/reports/info/"+this.props.medical_record_number;
			pu_href = "/patient/reports/pu/"+this.props.medical_record_number;
			events_href = "/patient/reports/events/"+this.props.medical_record_number;
			reposition_href = "/patient/reports/reposition/"+this.props.medical_record_number;
			alarm_response_href = "/patient/reports/alarm_response/"+this.props.medical_record_number;
			hide_list = "hide";
			offset_date = "offset-s3";
		}

		if(this.state.report_start > this.state.report_end) {
			cannot_filter = true;
			hide_button = "none";
			date_message = <span className="red-text" style={{fontSize: 80+"%"}}> * Please adjust date range</span>;
		}
		else if(this.state.report_start === sessionStorage['report_start'] && this.state.report_end === sessionStorage['report_end'] &&
			this.state.report_patient === sessionStorage['patient'] && this.state.report_unit === sessionStorage['unit'] &&
			this.state.report_view === sessionStorage['report_view'] && sessionStorage['active_report'] === this.state.report_active_member &&
			this.state.report_active_member === this.props.active_member && this.state.report_href == sessionStorage['report_href']) {
			cannot_filter = true;
			hide_button = "none";
		}
		else {
			cannot_filter = false;
			hide_button = "";
			date_message = "";
		}

		var active_units = new Set(); //temp store active units for comparison
		var disabled_units = [];//temp store disabled units
		var check_unit = this.state.report_unit;
		var patients_list = this.state.patient_list.map(function(p_name) {
			if(check_unit === p_name.unit_floor || check_unit === "All Units") {
				p_name.disabled = false;
				return p_name;
			}
			else {
				p_name.disabled = true;
				return p_name;
			}
		}).sort(function(a, b) {

			if(a.disabled && !b.disabled) return 1;
			if(b.disabled && !a.disabled) return -1;
			return 0;
		});
		active_units = Array.from(new Set(patients_list.map(function (patient) {
			return patient.unit_floor
		})));

		var unit_floor_list = this.state.available_unit_floors.map(function(u_name, index) {
			var active = false;
			for(var j = 0; j < active_units.length; j++) {
				if(active_units[j] === u_name) {
					active = true;
					break;
				}
			}
			if(active) {
				return (<option key={"unit_"+u_name}>{u_name}</option>);
			}
			else {
				disabled_units.push(<option key={"unit_"+u_name} disabled>{u_name} (0 Active Patients)</option>);
			}
		});

		unit_floor_list.push(disabled_units);

		//clear temporary arrays
		active_units = [];
		disabled_units = [];
		var button_style = {display: hide_button};

		return (
			<div>
				<form className="col s12" id="filter-form">
					<div className="row">
						<div className="input-field col s3">
							<select className="active" placeholder="Report View" id="report_view" name="report_view" value={this.state.report_view} onChange={this.onSelectionChange} >
								<option data-active_report="info" data-report_href={info_href} value="Patient Info">Patient Info</option>
								<option data-active_report="pu" data-report_href={pu_href} value="PU Status">PU Status</option>
								<option data-active_report="events" data-report_href={events_href} value="Events">Events</option>
								<option data-active_report="repositions" data-report_href={reposition_href} value="Reposition">Reposition</option>
								<option data-active_report="alarmresponses" data-report_href={alarm_response_href} value="Alarm Response">Alarm Response</option>
							</select>
							<label htmlFor="report_view">Select Report:</label>
						</div>
						<div className="input-field col s3" hidden={hide_list}>
							<select className="active" placeholder="Facility unit" id="report_unit" name="reports_unit" value={this.state.report_unit} onChange={this.onSelectionChange} >
								<option value="All Units">All Units</option>
								{unit_floor_list}
							</select>
							<label htmlFor="report_unit">Select Unit for Report:</label>
						</div>
						<div className="input-field col s3">
							<input placeholder="Start Date" id="report_start" name="report_start" defaultValue={this.state.report_start} type="date" className="datepicker" ref={function(ref) {if(!self.dates) {self.dates = []} self.dates.push(ref)}} />
							<label className="active" htmlFor="report_start">Start date for report: {date_message}</label>
						</div>
					</div>
					<div className="row">
						<div className="input-field col s3 offset-s3" hidden={hide_list}>
							<Select inputProps={{id:"report_patient"}} name="reports_patient" multi={true} options={patients_list} onChange={this.onPatientSelectionChange} value={this.state.report_mrn} />
							<label htmlFor="report_patient" className="active">Select Patient(s) for Report:</label>
						</div>
						<div className={"input-field col s3 "+offset_date} >
							<input placeholder="End Date" id="report_end" name="report_end" defaultValue={this.state.report_end} type="date" className="datepicker" ref={function(ref) {if(!self.dates) {self.dates = []} self.dates.push(ref)}} />
							<label className="active" htmlFor="report_end">End date for report: {date_message}</label>
						</div>
						<div className="input-field col s2" >
							<a id="filter-submit" className="filter-submit-button" type="submit" className="btn waves-effect waves-light" name="filter_submit" onClick={function(){if(!cannot_filter){self.onFilterClick()}}} href={this.state.report_href} style={button_style} disabled={cannot_filter}>Update</a>
						</div>
					</div>
				</form>
				{this.state.parameters_label}
			</div>
		);
	}
});

/********
 *
 * REPORTS
 *
 * ********/

var EventsReport = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
			hide_csv: "hide",
			loading: <div className="progress">
			<div className="indeterminate"></div>
		</div>,
		};
	},

	getEventsCSV: function() {
		var self = this;
		var csvurl = "";
		var win = window.open('');

		window.oldOpen = window.open;
		window.open = function(url) { // reassignment function
			win.location = url;
			window.open = oldOpen;
			win.focus();
		}
		$.ajax(
			{
				url: "/api/"+config.APIVersion+"/download-token",
				method: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}
		).done(function(data) {
			var csvargs = "?format=csv&token="+data.token+"&email="+data.email+"&expiration="+data.expiration;
			var url_paramaters = "&start="+sessionStorage['utc_report_start']+"&end="+sessionStorage['utc_report_end'];
			if(sessionStorage['unit'] !== "All Units") {
				url_paramaters = url_paramaters+"&unit_floor="+sessionStorage['unit'];
			}
			csvurl = "/api/"+config.APIVersion+"/eventreports"+csvargs+url_paramaters;
			if(self.props.medical_record_number) {
				csvurl = "/api/"+config.APIVersion+"/eventreports/"+self.props.medical_record_number+csvargs+url_paramaters;
			}
			else if(sessionStorage['patient_mrn'] && sessionStorage['patient_mrn'] !== undefined && sessionStorage['patient_mrn'] !== null && sessionStorage['patient_mrn'] !== "" && sessionStorage['patient'] !== "All Patients") {
				csvurl = "/api/"+config.APIVersion+"/eventreports/"+sessionStorage['patient_mrn']+csvargs+url_paramaters;
			}
			window.open("https://"+window.location.hostname+csvurl);
		});
	},

	onSubmit: function() {
		this.setState({
			loading: <div className="progress">
				<div className="indeterminate"></div>
			</div>,
		});
		if(sessionStorage['active_report'] === "events") {
			this.reportTable();
		}
		else {
			this.setState({loading: "Please update your search",});
		}
	},

	reportTable: function(event) {
		var self = this;
		var url_paramaters = "?start="+sessionStorage['utc_report_start']+"&end="+sessionStorage['utc_report_end'];
		if(sessionStorage['unit'] !== "All Units") {
			url_paramaters = url_paramaters+"&unit_floor="+sessionStorage['unit'];
		}
		var url = "/api/"+config.APIVersion+"/eventreports"+url_paramaters;
		if(this.props.medical_record_number) {
			url = "/api/"+config.APIVersion+"/eventreports/"+this.props.medical_record_number+url_paramaters;
		}
		else if(sessionStorage['patient_mrn'] && sessionStorage['patient_mrn'] !== undefined && sessionStorage['patient_mrn'] !== null && sessionStorage['patient_mrn'] !== "" && sessionStorage['patient'] !== "All Patients") {
			url = "/api/"+config.APIVersion+"/eventreports/"+sessionStorage['patient_mrn']+url_paramaters;
		}
		self.setState({
			state: 'looking up events...',
		});
		$.ajax(
			{
				url: url,
				method: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					},
					404: function() {
						self.setState({
							state: 'idle',
							hide_csv: "hide",
							loading: "No report available",
						});
					}
				},
			}
		).done(function(data) {
			$('#report-warning').css('display', 'none');
			self.setState({
				state: 'idle',
				hide_csv: "",
				loading: "No reports for patient events available",
			});

			$("#get_events_csv").click(function() {
				self.getEventsCSV();
			});

			if(data === [] || data === "" || data === undefined ||  data.event_reports.length <= 0) {
				self.setState({hide_csv: "hide"});
				return;
			}

			for(var i=0; i < data.event_reports.length; i++) {
				var loc = data.event_reports[i].location+"";
				loc = loc.replace("_"," ").toLowerCase();
				var newloc = loc.charAt(0).toUpperCase() + loc.slice(1);
				if(newloc === "Undefined") {
					newloc = "N/A";
				}

				var occurred = data.event_reports[i].occurred+"";
				occurred = moment(occurred).format('YYYY-MM-DD, h:mm:ss a');

				data.event_reports[i].location = newloc;
				data.event_reports[i].occurred = occurred;

				var sens = data.event_reports[i].sensor_serial;
				if(sens) {
					data.event_reports[i].sensor_serial = sens.replace("0x","");
				}
			}

			self.setState({loading: ""});
			var hot = new Handsontable(document.getElementById("events-container"), {
				data: data.event_reports,
				fixedRowsTop: 0,
				columnSorting: true,
				maxRows: MAX_REPORT_ENTRIES,
				renderAllRows: true,
				sortIndicator: true,
				fixedColumnsLeft: 2,
				colHeaders: ["Unit/Floor", "Patient Name", "Patient Last Name", "Event Type", "Event Occurred", "Body Location", "Sensor ID", "Sensor Distance", "Alarm Threshold (minutes)","Alarm Clear Multiple", "Previous Alarm Indicator Duration (hours)"],
				columns: [
					{data: 'unit_floor', editor: false},
					{data: 'name', editor: false},
					{data: 'last_name', editor: false},
					{data: 'event_type', editor: false},
					{data: 'occurred', type: "date", readOnly: true, editor: false},
					{data: 'location', editor: false},
					{data: 'sensor_serial', editor: false},
					{data: 'distance', editor: false},
					{data: 'alarm_threshold_minutes', editor: false},
					{data: 'alarm_clear_multiple', editor: false},
					{data: 'previous_alarm_threshold_hours', editor: false},
				],
			});
			if (data.total_amount > MAX_REPORT_ENTRIES) {
				self.setState({total_rows: data.total_amount});
				$('#report-warning').css('display', 'block');
			}
			else {
				$('#report-warning').css('display', 'none');
			}
		});
	},

	handleFilterChange: function() {
		if(this.state.state === "idle") {
			this.onSubmit();
		}
	},

	componentDidMount: function() {
		// subscribe to date filter changes
		window.addEventListener('filterChange', this.handleFilterChange);
		this.onSubmit();
	},

	componentWillUnmount: function() {
		window.removeEventListener('filterChange', this.handleFilterChange);
		$("#get_events_csv").unbind("click");
	},

	render: function() {
		var stylee = {height: 700+'px', width: 100+'%', overflow: "scroll", overflowX: "hidden", overflowY: "scroll", fontSize: 80+"%"};
		return (
			<div>
				<ReportsNav active_member="events" medical_record_number={this.props.medical_record_number}/>
				<div className="yellow" id="report-warning">Only first 1000 of total { this.state.total_rows } entries are shown. To get the entire report, download the report</div>
				<div id="events-container" style={stylee}>
					{this.state.loading}
				</div>
				<div className={"top-right-button "+this.state.hide_csv}>
					<a id="get_events_csv" href="">
						<img height="24" src={excel_icon}></img>
						<span>Download Spreadsheet</span>
					</a>
				</div>
			</div>
		);
	}
});

var PatientInfoReport = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
			hide_csv: "hide",
			loading: <div className="progress">
			<div className="indeterminate"></div>
		</div>,
		};
	},

	onSubmit: function() {
		this.setState({
			loading: <div className="progress">
				<div className="indeterminate"></div>
			</div>,
		});
		if(sessionStorage['active_report'] === "info") {
			this.reportTable();
		}
		else {
			this.setState({loading: "Please update your search",});
		}
	},

	reportTable: function(event) {
		var self = this;
		var url_paramaters = "?start="+sessionStorage['utc_report_start']+"&end="+sessionStorage['utc_report_end'];
		if(sessionStorage['unit'] !== "All Units") {
			url_paramaters = url_paramaters+"&unit_floor="+sessionStorage['unit'];
		}
		var url = "/api/"+config.APIVersion+"/patientinforeports"+url_paramaters;
		if(this.props.medical_record_number) {
			url = "/api/"+config.APIVersion+"/patientinforeports/"+this.props.medical_record_number+url_paramaters;
		}
		else if(sessionStorage['patient_mrn'] && sessionStorage['patient_mrn'] !== undefined && sessionStorage['patient_mrn'] !== null && sessionStorage['patient_mrn'] !== "" && sessionStorage['patient'] !== "All Patients") {
			url = "/api/"+config.APIVersion+"/patientinforeports/"+sessionStorage['patient_mrn']+url_paramaters;
		}
		self.setState({
			state: 'looking up users...',
			users: self.state.users
		});
		$.ajax(
			{
				url: url,
				method: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					},
					404: function() {
						self.setState({
							state: 'idle',
							hide_csv: "hide",
							loading: "No report available",
						});
					}

				},
			}
		).done(function(data) {
			$('#report-warning').css('display', 'none');
			self.setState({
				state: 'idle',
				hide_csv: "",
				loading: "No patient reports available",
			});

			$("#get_patients_csv").click(function() {
				self.getPatientsCSV();
			});

			if(data === [] || data === "" || data === undefined ||  data.patient_reports.length <= 0) {
				self.setState({hide_csv: "hide"});
				return;
			}

			for(var i=0; i < data.patient_reports.length; i++) {
				var occurred = data.patient_reports[i].date_of_record+"";
				occurred = moment(occurred).format('YYYY-MM-DD, h:mm:ss a');
				data.patient_reports[i].date_of_record = occurred;
			}

			self.setState({loading: ""});
			var hot = new Handsontable(document.getElementById("patient-info-container"), {
				data: data.patient_reports,
				colHeaders: ["Patient Name", "Patient Last Name", "Date of Record", "Username", "Gender", "DOB", "Date of Admission", "Units", "Unit/Floor", "Bed Type", "Ethnicity", "Braden Score", "Mobility", "Diagnosis", "Medication", "Weight", "Height", "BMI", "Albumin Level", "A1C", "Hemoglobin", "O2 Saturation", "Blood Pressure"],
				fixedRowsTop: 0,
				renderAllRows: true,
				maxRows: MAX_REPORT_ENTRIES,
				fixedColumnsLeft: 1,
				columns: [
					{data: 'name', editor: false},
					{data: 'last_name', editor: false},
					{data: 'date_of_record', type: 'date', readOnly: true, editor: false},
					{data: 'username', editor: false},
					{data: 'gender', editor: false},
					{data: 'DOB', editor: false},
					{data: 'date_of_admission', type: 'date', readOnly: true, editor: false},
					{data: 'units', editor: false},
					{data: 'unit_floor', editor: false},
					{data: 'bed_type', editor: false},
					{data: 'ethnicity', editor: false},
					{data: 'braden_score', editor: false},
					{data: 'mobility', editor: false},
					{data: 'diagnosis', editor: false},
					{data: 'medication', editor: false},
					{data: 'weight', editor: false},
					{data: 'height', editor: false},
					{data: 'bmi', editor: false},
					{data: 'albumin_level', editor: false},
					{data: 'A1C', editor: false},
					{data: 'hemoglobin', editor: false},
					{data: 'o2_saturation', editor: false},
					{data: 'blood_pressure', editor: false},
				],
				columnSorting: true
			});
			if (data.total_amount > MAX_REPORT_ENTRIES) {
				$('#report-warning').css('display', 'block');
				self.setState({total_rows: data.total_amount});
			}
			else {
				$('#report-warning').css('display', 'none');
			}
		});
	},

	getPatientsCSV: function() {
		var self = this;
		var csvurl = "";
		var win = window.open('');
		window.oldOpen = window.open;
		window.open = function(url) { // reassignment function
			win.location = url;
			window.open = oldOpen;
			win.focus();
		}
		$.ajax(
			{
				url: "/api/"+config.APIVersion+"/download-token",
				method: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}
		).done(function(data) {
			var csvargs = "?format=csv&token="+data.token+"&email="+data.email+"&expiration="+data.expiration;
			var url_paramaters = "&start="+sessionStorage['utc_report_start']+"&end="+sessionStorage['utc_report_end'];
			if(sessionStorage['unit'] !== "All Units") {
				url_paramaters = url_paramaters+"&unit_floor="+sessionStorage['unit'];
			}
			csvurl = "/api/"+config.APIVersion+"/patientinforeports"+csvargs+url_paramaters;
			if(self.props.medical_record_number) {
				csvurl = "/api/"+config.APIVersion+"/patientinforeports/"+self.props.medical_record_number+csvargs+url_paramaters;
			}
			else if(sessionStorage['patient_mrn'] && sessionStorage['patient_mrn'] !== undefined && sessionStorage['patient_mrn'] !== null && sessionStorage['patient_mrn'] !== "" && sessionStorage['patient'] !== "All Patients") {
				csvurl = "/api/"+config.APIVersion+"/patientinforeports/"+sessionStorage['patient_mrn']+csvargs+url_paramaters;
			}
			window.open("https://"+window.location.hostname+csvurl);
		});
	},

	handleFilterChange: function() {
		if(this.state.state === "idle") {
			this.onSubmit();
		}
	},

	componentWillUnmount: function() {
		window.removeEventListener('filterChange', this.handleFilterChange);
		$("#get_patients_csv").unbind("click");
	},

	componentDidMount: function() {
		// subscribe to date filter changes
		window.addEventListener('filterChange', this.handleFilterChange);
		this.onSubmit();
	},

	render: function() {
		var stylee = {height: 700+'px', width: 100+'%', overflow: "scroll", overflowX: "hidden", overflowY: "scroll", fontSize: 80+"%"};
		return (
			<div>
				<ReportsNav active_member="info" medical_record_number={this.props.medical_record_number}/>
				<div className="yellow" id="report-warning">Only first 1000 of total { this.state.total_rows } entries are shown. To get the entire report, download the report</div>
				<div id="patient-info-container" style={stylee}>
					{this.state.loading}
				</div>
				<div className={"top-right-button "+this.state.hide_csv}>
					<a id="get_patients_csv" href="">
						<img height="24" src={excel_icon}></img>
						<span>Download Spreadsheet</span>
					</a>
				</div>
			</div>
		);
	}
});

var PUStatusReport = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
			hide_csv: "hide",
			loading: <div className="progress">
			<div className="indeterminate"></div>
		</div>,
		};
	},

	getPUCSV: function() {
		var self = this;
		var csvurl = "";
		var win = window.open('');

		window.oldOpen = window.open;
		window.open = function(url) { // reassignment function
			win.location = url;
			window.open = oldOpen;
			win.focus();
		}
		$.ajax(
			{
				url: "/api/"+config.APIVersion+"/download-token",
				method: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}
		).done(function(data) {
			var csvargs = "?format=csv&token="+data.token+"&email="+data.email+"&expiration="+data.expiration;
			var url_paramaters = "&start="+sessionStorage['utc_report_start']+"&end="+sessionStorage['utc_report_end'];
			if(sessionStorage['unit'] !== "All Units") {
				url_paramaters = url_paramaters+"&unit_floor="+sessionStorage['unit'];
			}
			csvurl = "/api/"+config.APIVersion+"/pustatusreports"+csvargs+url_paramaters;
			if(self.props.medical_record_number) {
				csvurl = "/api/"+config.APIVersion+"/pustatusreports/"+self.props.medical_record_number+csvargs+url_paramaters;
			}
			else if(sessionStorage['patient_mrn'] && sessionStorage['patient_mrn'] !== undefined && sessionStorage['patient_mrn'] !== null && sessionStorage['patient_mrn'] !== "" && sessionStorage['patient'] !== "All Patients") {
				csvurl = "/api/"+config.APIVersion+"/pustatusreports/"+sessionStorage['patient_mrn']+csvargs+url_paramaters;
			}
			window.open("https://"+window.location.hostname+csvurl);
		});
	},

	onSubmit: function() {
		this.setState({
			loading: <div className="progress">
				<div className="indeterminate"></div>
			</div>,
		});
		if(sessionStorage['active_report'] === "pu") {
			this.reportTable();
		}
		else {
			this.setState({loading: "Please update your search",});
		}
	},

	reportTable: function(event) {
		var self = this;
		var url_paramaters = "?start="+sessionStorage['utc_report_start']+"&end="+sessionStorage['utc_report_end'];
		if(sessionStorage['unit'] !== "All Units") {
			url_paramaters = url_paramaters+"&unit_floor="+sessionStorage['unit'];
		}
		var url = "/api/"+config.APIVersion+"/pustatusreports"+url_paramaters;
		if(this.props.medical_record_number) {
			url = "/api/"+config.APIVersion+"/pustatusreports/"+this.props.medical_record_number+url_paramaters;
		}
		else if(sessionStorage['patient_mrn'] && sessionStorage['patient_mrn'] !== undefined && sessionStorage['patient_mrn'] !== null && sessionStorage['patient_mrn'] !== "" && sessionStorage['patient'] !== "All Patients") {
			url = "/api/"+config.APIVersion+"/pustatusreports/"+sessionStorage['patient_mrn']+url_paramaters;
		}
		self.setState({
			state: 'looking up PU statuses...',
		});
		$.ajax(
			{
				url: url,
				method: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					},
					404: function() {
						self.setState({
							state: 'idle',
							hide_csv: "hide",
							loading: "No report available",
						});
					}
				},
			}
		).done(function(data) {
			$('#report-warning').css('display', 'none');
			self.setState({
				state: 'idle',
				data: data,
				hide_csv: "",
				loading: "No pressure ulcer reports available",
			});

			$("#get_pu_csv").click(function() {
				self.getPUCSV();
			});

			if(data === [] || data === "" || data === undefined ||  data.pu_status_reports.length <= 0) {
				self.setState({hide_csv: "hide"});
				return;
			}

			for(var i=0; i < data.pu_status_reports.length; i++) {
				var loc = data.pu_status_reports[i].location+"";
				loc = loc.replace("_"," ").toLowerCase();
				var newloc = loc.charAt(0).toUpperCase() + loc.slice(1);
				if(newloc === "Undefined") {
					newloc = "N/A";
				}
				data.pu_status_reports[i].location = newloc;

				var eloc = data.pu_status_reports[i].existing_wound_location+"";
				eloc = eloc.replace("_"," ").toLowerCase();
				var enewloc = eloc.charAt(0).toUpperCase() + eloc.slice(1);
				if(enewloc === "Undefined") {
					enewloc = "N/A";
				}
				data.pu_status_reports[i].existing_wound_location = enewloc;

				var occurred = data.pu_status_reports[i].wound_existing_since+"";
				occurred = moment.utc(occurred).format('YYYY-MM-DD');

				data.pu_status_reports[i].wound_existing_since = occurred;
			}

			self.setState({loading: ""});
			var hot = new Handsontable(document.getElementById("pu-status-container"), {
				data: data.pu_status_reports,
				fixedRowsTop: 0,
				renderAllRows: true,
				maxRows: MAX_REPORT_ENTRIES,
				fixedColumnsLeft: 1,
				stretchH: "all",
				colHeaders: ["Patient Name", "Patient Last Name", "Wound Location", "Existing Wound", "Date of Record", "Wound Stage", "Existing Wound Location", "Existing Wound Measurement"],
				columns: [
					{data: 'name', editor: false},
					{data: 'last_name', editor: false},
					{data: 'location', editor: false},
					{data: 'existing_wound', editor: false},
					{data: 'wound_existing_since', type: 'date', readOnly: true, editor: false},
					{data: 'wound_stage', editor: false},
					{data: 'existing_wound_location', editor: false},
					{data: 'wound_measurement', editor: false},
				],
				columnSorting: true
			});
			if (data.total_amount > MAX_REPORT_ENTRIES) {
				$('#report-warning').css('display', 'block');
				self.setState({total_rows: data.total_amount});
			}
			else {
				$('#report-warning').css('display', 'none');
			}
		});
	},

	handleFilterChange: function() {
		if(this.state.state === "idle") {
			this.onSubmit();
		}
	},

	componentDidMount: function() {
		// subscribe to date filter changes
		window.addEventListener('filterChange', this.handleFilterChange);
		this.onSubmit();
	},

	componentWillUnmount: function() {
		window.removeEventListener('filterChange', this.handleFilterChange);
		$("#get_events_csv").unbind("click");
	},

	render: function() {
		var stylee = {height: 700+'px', width: 100+'%', overflow: "scroll", overflowX: "hidden", overflowY: "scroll", fontSize: 80+"%"};
		return (
			<div>
				<ReportsNav active_member="pu" medical_record_number={this.props.medical_record_number}/>
				<div className="yellow" id="report-warning">Only first 1000 of total { this.state.total_rows } entries are shown. To get the entire report, download the report</div>
				<div id="pu-status-container" style={stylee}>
					{this.state.loading}
				</div>
				<div className={"top-right-button "+this.state.hide_csv}>
					<a id="get_pu_csv" href="">
						<img height="24" src={excel_icon}></img>
						<span>Download Spreadsheet</span>
					</a>
				</div>
			</div>
		);
	}
});

var RepositionReport = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
			hide_csv: "hide",
			loading: <div className="progress">
			<div className="indeterminate"></div>
		</div>,
		};
	},

	onSubmit: function() {
		this.setState({
			loading: <div className="progress">
				<div className="indeterminate"></div>
			</div>,
		});
		if(sessionStorage['active_report'] === "repositions") {
			this.reportTable();
		}
		else {
			this.setState({loading: "Please update your search",});
		}
	},

	reportTable: function(event) {
		var self = this;

		var url_paramaters = "?start="+sessionStorage['utc_report_start']+"&end="+sessionStorage['utc_report_end'];
		if(sessionStorage['unit'] !== "All Units" && !this.props.medical_record_number && sessionStorage['patient'] === "All Patients" ) {
			url_paramaters = url_paramaters+"&unit_floor="+sessionStorage['unit'];
		}
		var url = "/api/"+config.APIVersion+"/repositionreports"+url_paramaters;
		if(this.props.medical_record_number && sessionStorage['unit'] === "All Units") {
			url = "/api/"+config.APIVersion+"/repositionreports/"+this.props.medical_record_number+"/"+url_paramaters;
		}
		else if(sessionStorage['patient_mrn'] && sessionStorage['patient_mrn'] !== undefined && sessionStorage['patient_mrn'] !== null && sessionStorage['patient_mrn'] !== "" && sessionStorage['patient'] !== "All Patients") {
			url = "/api/"+config.APIVersion+"/repositionreports/"+sessionStorage['patient_mrn']+"/"+url_paramaters;
		}
		self.setState({
			state: 'looking up reposition reports...',
		});
		$.ajax(
			{
				url: url,
				method: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					},
					404: function() {
						self.setState({
							state: 'idle',
							hide_csv: "hide",
							loading: "No report available",
						});
					}
				},
			}
		).done(function(data) {
			$('#report-warning').css('display', 'none');
			self.setState({
				state: 'idle',
				hide_csv: "",
				loading: "No reposition reports available",
			});

			$("#get_reposition_csv").click(function() {
				self.getRepositionCSV();
			});

			if(data === [] || data === "" || data === undefined || data.reposition_reports.length <= 0) {
				self.setState({hide_csv: "hide"});
				return;
			}

			self.setState({loading: ""});
			var hot = new Handsontable(document.getElementById("reposition-container"), {
				data: data.reposition_reports,
				fixedRowsTop: 0,
				fixedColumnsLeft: 2,
				maxRows: MAX_REPORT_ENTRIES,
				renderAllRows: true,
				className: "htCenter",
				colHeaders: ["Date", "Description", "0:00h", "1:00h", "2:00h", "3:00h", "4:00h", "5:00h", "6:00h", "7:00h", "8:00h", "9:00h", "10:00h", "11:00h", "12:00h", "13:00h", "14:00h", "15:00h", "16:00h", "17:00h", "18:00h", "19:00h", "20:00h", "21:00h", "22:00h", "23:00h", "Daily Average", "Total"],
				columns: [
					{data: 'date', className: "htLeft", editor: false},
					{data: 'description', className: "htLeft", editor: false},
					{data: 'hour0', editor: false},
					{data: 'hour1', editor: false},
					{data: 'hour2', editor: false},
					{data: 'hour3', editor: false},
					{data: 'hour4', editor: false},
					{data: 'hour5', editor: false},
					{data: 'hour6', editor: false},
					{data: 'hour7', editor: false},
					{data: 'hour8', editor: false},
					{data: 'hour9', editor: false},
					{data: 'hour10', editor: false},
					{data: 'hour11', editor: false},
					{data: 'hour12', editor: false},
					{data: 'hour13', editor: false},
					{data: 'hour14', editor: false},
					{data: 'hour15', editor: false},
					{data: 'hour16', editor: false},
					{data: 'hour17', editor: false},
					{data: 'hour18', editor: false},
					{data: 'hour19', editor: false},
					{data: 'hour20', editor: false},
					{data: 'hour21', editor: false},
					{data: 'hour22', editor: false},
					{data: 'hour23', editor: false},
					{data: 'daily_average', editor: false},
					{data: 'total', editor: false},
				],
				columnSorting: true
			});
			if (data.total_amount > MAX_REPORT_ENTRIES) {
				$('#report-warning').css('display', 'block');
				self.setState({total_rows: data.total_amount});
			}
			else {
				$('#report-warning').css('display', 'none');
			}
		});
	},

	getRepositionCSV: function() {
		var self = this;
		var csvurl = "";
		var win = window.open('');
		window.oldOpen = window.open;
		window.open = function(url) { // reassignment function
			win.location = url;
			window.open = oldOpen;
			win.focus();
		}
		$.ajax(
			{
				url: "/api/"+config.APIVersion+"/download-token",
				method: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}
		).done(function(data) {
			var csvargs = "?format=csv&token="+data.token+"&email="+data.email+"&expiration="+data.expiration;
			var url_paramaters = "&start="+sessionStorage['utc_report_start']+"&end="+sessionStorage['utc_report_end'];
			if(sessionStorage['unit'] !== "All Units" && !this.props.medical_record_number && sessionStorage['patient'] === "All Patients" ) {
				url_paramaters = url_paramaters+"&unit_floor="+sessionStorage['unit'];
			}
			csvurl = "/api/"+config.APIVersion+"/repositionreports"+csvargs+url_paramaters;
			if(self.props.medical_record_number) {
				csvurl = "/api/"+config.APIVersion+"/repositionreports/"+self.props.medical_record_number+"/"+csvargs+url_paramaters;
			}
			else if(sessionStorage['patient_mrn'] && sessionStorage['patient_mrn'] !== undefined && sessionStorage['patient_mrn'] !== null && sessionStorage['patient_mrn'] !== "" && sessionStorage['patient'] !== "All Patients") {
				csvurl = "/api/"+config.APIVersion+"/repositionreports/"+sessionStorage['patient_mrn']+"/"+csvargs+url_paramaters;
			}
			window.open("https://"+window.location.hostname+csvurl);
		});
	},

	handleFilterChange: function() {
		if(this.state.state === "idle") {
			this.onSubmit();
		}
	},

	componentWillUnmount: function() {
		window.removeEventListener('filterChange', this.handleFilterChange);
		$("#get_reposition_csv").unbind("click");
	},

	reportHelpContent: function() {
		var url = "/xajax/help/report-reposition.md";
		$.ajax(
				{
					url: url,
					beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
					statusCode: {
						401: function() {
							navigate(config.baseUrl+"/logout");
						}
					},
				}).done(function(data){
					$("#help-modal-text").html(marked(data));
					$("#help-btn").click(function() {
                        $('#help-modal').modal();
						$('#help-modal').modal('open');
					});
				});
	},

	componentDidMount: function() {
		// subscribe to date filter changes
		window.addEventListener('filterChange', this.handleFilterChange);
		this.onSubmit();
		this.reportHelpContent();
	},

	render: function() {
		var stylee = {height: 700+'px', width: 100+'%', overflow: "scroll", overflowX: "hidden", overflowY: "scroll", fontSize: 80+"%"};
		return (
			<div>
				<ReportsNav active_member="repositions" medical_record_number={this.props.medical_record_number}/>
				<div id="help-modal" className="modal">
					<div className="modal-content">
						<h5 id="help-modal-title">Reposition Help</h5>
						<div id="help-modal-text">.</div>
					</div>
					<div className="modal-footer">
						<a href="#!" className=" modal-action modal-close waves-effect waves-green btn-flat">Close</a>
					</div>
				</div>
				<a href="#" id="help-btn"><i className="tiny material-icons">info_outline</i> Report Help</a>
				<div className="yellow" id="report-warning">Only first 1000 of total { this.state.total_rows } entries are shown. To get the entire report, download the report</div>
				<div id="reposition-container" style={stylee}>
					{this.state.loading}
				</div>
				<div className={"top-right-button "+this.state.hide_csv}>
					<a id="get_reposition_csv" href="">
						<img height="24" src={excel_icon}></img>
						<span>Download Spreadsheet</span>
					</a>
				</div>
			</div>
		);
	}
});

var AlarmResponseReport = React.createClass({
	getInitialState: function() {
		return {
			state: 'idle',
			hide_csv: "hide",
			loading: <div className="progress">
			<div className="indeterminate"></div>
		</div>,
		};
	},

	onSubmit: function() {
		this.setState({
			loading: <div className="progress">
				<div className="indeterminate"></div>
			</div>,
		});
		if(sessionStorage['active_report'] === "alarmresponses") {
			this.reportTable();
		}
		else {
			this.setState({loading: "Please update your search",});
		}
	},

	reportTable: function(event) {
		var self = this;
		var url_paramaters = "?start="+sessionStorage['utc_report_start']+"&end="+sessionStorage['utc_report_end'];
		if(sessionStorage['unit'] !== "All Units" && !this.props.medical_record_number && sessionStorage['patient'] === "All Patients" ) {
			url_paramaters = url_paramaters+"&unit_floor="+sessionStorage['unit'];
		}
		var url = "/api/"+config.APIVersion+"/alarmresponsereports"+url_paramaters;
		if(this.props.medical_record_number) {
			url = "/api/"+config.APIVersion+"/alarmresponsereports/"+this.props.medical_record_number+"/"+url_paramaters;
		}
		else if(sessionStorage['patient_mrn'] && sessionStorage['patient_mrn'] !== undefined && sessionStorage['patient_mrn'] !== null && sessionStorage['patient_mrn'] !== "" && sessionStorage['patient'] !== "All Patients") {
			url = "/api/"+config.APIVersion+"/alarmresponsereports/"+sessionStorage['patient_mrn']+"/"+url_paramaters;
		}
		self.setState({
			state: 'looking up alarm response reports...',
		});
		$.ajax(
			{
				url: url,
				method: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					},
					404: function() {
						self.setState({
							state: 'idle',
							hide_csv: "hide",
							loading: "No report available",
						});
					}
				},
			}
		).done(function(data) {
			$('#report-warning').css('display', 'none');
			self.setState({
				state: 'idle',
				hide_csv: "",
				loading: "No alarm reponse reports available",
			});

			$("#get_alarm_response_csv").click(function() {
				self.getAlarmResponseCSV();
			});

			if(data === [] || data === "" || data === undefined || data.alarm_response_reports.length <= 0) {
				self.setState({hide_csv: "hide"});
				return;
			}

			self.setState({loading: ""});
			var hot = new Handsontable(document.getElementById("alarm-response-container"), {
				data: data.alarm_response_reports,
				fixedRowsTop: 0,
				fixedColumnsLeft: 2,
				renderAllRows: true,
				maxRows: MAX_REPORT_ENTRIES,
				className: "htCenter",
				colHeaders: ["Date", "Description", "0:00h", "1:00h", "2:00h", "3:00h", "4:00h", "5:00h", "6:00h", "7:00h", "8:00h", "9:00h", "10:00h", "11:00h", "12:00h", "13:00h", "14:00h", "15:00h", "16:00h", "17:00h", "18:00h", "19:00h", "20:00h", "21:00h", "22:00h", "23:00h", "Daily Average", "Total"],
				columns: [
					{data: 'date', className: "htLeft", editor: false},
					{data: 'description', className: "htLeft", editor: false},
					{data: 'hour0', editor: false},
					{data: 'hour1', editor: false},
					{data: 'hour2', editor: false},
					{data: 'hour3', editor: false},
					{data: 'hour4', editor: false},
					{data: 'hour5', editor: false},
					{data: 'hour6', editor: false},
					{data: 'hour7', editor: false},
					{data: 'hour8', editor: false},
					{data: 'hour9', editor: false},
					{data: 'hour10', editor: false},
					{data: 'hour11', editor: false},
					{data: 'hour12', editor: false},
					{data: 'hour13', editor: false},
					{data: 'hour14', editor: false},
					{data: 'hour15', editor: false},
					{data: 'hour16', editor: false},
					{data: 'hour17', editor: false},
					{data: 'hour18', editor: false},
					{data: 'hour19', editor: false},
					{data: 'hour20', editor: false},
					{data: 'hour21', editor: false},
					{data: 'hour22', editor: false},
					{data: 'hour23', editor: false},
					{data: 'daily_average', editor: false},
					{data: 'total', editor: false},
				],
				columnSorting: true
			});

			if (data.total_amount > MAX_REPORT_ENTRIES) {
				$('#report-warning').css('display', 'block');
				self.setState({total_rows: data.total_amount});
			}
			else {
				$('#report-warning').css('display', 'none');
			}
		});
	},

	reportHelpContent: function() {
		var url = "/xajax/help/report-alarm-response.md";
		$.ajax(
			{
				url: url,
				beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						navigate(config.baseUrl+"/logout");
					}
				},
			}).done(function(data){
				$("#help-modal-text").html(marked(data));
					$("#help-btn").click(function() {
						$('#help-modal').modal();
						$('#help-modal').modal('open');
					});
				});
	},

	getAlarmResponseCSV: function() {
		var self = this;
		var csvurl = "";
		var win = window.open('');
		window.oldOpen = window.open;
		window.open = function(url) { // reassignment function
			win.location = url;
			window.open = oldOpen;
			win.focus();
		}
		$.ajax(
			{
				url: "/api/"+config.APIVersion+"/download-token",
				method: 'GET',
				beforeSend: function(xhr) {xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
				statusCode: {
					401: function() {
						$.navigate(config.baseUrl+"/logout");
					}
				},
			}
		).done(function(data) {
			var csvargs = "?format=csv&token="+data.token+"&email="+data.email+"&expiration="+data.expiration;
			var url_paramaters = "&start="+sessionStorage['utc_report_start']+"&end="+sessionStorage['utc_report_end'];
			if(sessionStorage['unit'] !== "All Units" && !this.props.medical_record_number && sessionStorage['patient'] === "All Patients" ) {
				url_paramaters = url_paramaters+"&unit_floor="+sessionStorage['unit'];
			}
			csvurl = "/api/"+config.APIVersion+"/alarmresponsereports"+csvargs+url_paramaters;
			if(self.props.medical_record_number) {
				csvurl = "/api/"+config.APIVersion+"/alarmresponsereports/"+self.props.medical_record_number+"/"+csvargs+url_paramaters;
			}
			else if(sessionStorage['patient_mrn'] && sessionStorage['patient_mrn'] !== undefined && sessionStorage['patient_mrn'] !== null && sessionStorage['patient_mrn'] !== "" && sessionStorage['patient'] !== "All Patients") {
				csvurl = "/api/"+config.APIVersion+"/alarmresponsereports/"+sessionStorage['patient_mrn']+"/"+csvargs+url_paramaters;
			}
			window.open("https://"+window.location.hostname+csvurl);
		});
	},

	handleFilterChange: function() {
		if(this.state.state === "idle") {
			this.onSubmit();
		}
	},

	componentWillUnmount: function() {
		window.removeEventListener('filterChange', this.handleFilterChange);
		$("#get_alarm_response_csv").unbind("click");
	},

	componentDidMount: function() {
		// subscribe to date filter changes
		window.addEventListener('filterChange', this.handleFilterChange);
		this.onSubmit();
		this.reportHelpContent();
	},

	render: function() {
		var stylee = {height: 700+'px', width: 100+'%', overflow: "scroll", overflowX: "hidden", overflowY: "scroll", fontSize: 80+"%"};
		return (
			<div>
				<ReportsNav active_member="alarmresponses" medical_record_number={this.props.medical_record_number}/>
				<div id="help-modal" className="modal">
					<div className="modal-content">
						<h5 id="help-modal-title">Alarm Response Help</h5>
						<div id="help-modal-text">.</div>
					</div>
					<div className="modal-footer">
						<a href="#!" className=" modal-action modal-close waves-effect waves-green btn-flat">Close</a>
					</div>
				</div>
				<a href="#" id="help-btn"><i className="tiny material-icons">info_outline</i> Report Help</a>
				<div className="yellow" id="report-warning">Only first 1000 of total { this.state.total_rows } entries are shown. To get the entire report, download the report</div>
				<div id="alarm-response-container" style={stylee}>
					{this.state.loading}
				</div>
				<div className={"top-right-button "+this.state.hide_csv}>
					<a id="get_alarm_response_csv" href="">
						<img height="24" src={excel_icon}></img>
						<span>Download Spreadsheet</span>
					</a>
				</div>
			</div>
		);
	}
});

export {PUStatusReport, EventsReport, PatientInfoReport, RepositionReport, AlarmResponseReport};

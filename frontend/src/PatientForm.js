import React from 'react';
import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');

var PatientForm = React.createClass({
	getInitialState: function() {
		return {
			medication: [
				{"display_name": "None", "name": "none", "value": true},
				{"display_name": "Steroids", "name": "steroids", "value": false},
				{"display_name": "Vasopressors", "name": "vasopressors", "value": false},
				{"display_name": "Heart rhythm", "name": "heart_rhythm", "value": false},
				{"display_name": "Blood pressure", "name": "blood_pressure", "value": false},
				{"display_name": "Narcotic pain control", "name": "narcotic_pain", "value": false},
				{"display_name": "Non-narcotic pain", "name": "non_narcotic_pain", "value": false},
				{"display_name": "Hypoglycemic", "name": "hypoglycemic", "value": false},
				{"display_name": "Sleeping", "name": "sleeping", "value": false},
				{"display_name": "Constipation relief", "name": "constipation_relief", "value": false},
				{"display_name": "Anxiety control", "name": "anxiety_control", "value": false},
				{"display_name": "Antispasmodics", "name": "antispasmodics", "value": false},
				{"display_name": "Antibiotics", "name": "antibiotics", "value": false},
				{'name': 'chemotherapy', 'display_name': 'Chemotherapy', "value": false},
				{'name': 'radiation', 'display_name': 'Radiation', "value": false},
				{"display_name": "Other", "name": "other", "value": false}
			],

			diagnosis: [
				{"display_name":"Diabetes","name":"diabetes","value": false  },
				{"display_name":"Heart Disease","name":"heart_disease","value": false  },
				{"display_name":"Stroke","name":"stroke","value": false  },
				{"display_name":"Immobility (stroke, paraplegic, quadriplegic)","name":"immobility","value": false  },
				{"display_name":"PVD (peripheral vascular disease)","name":"pvd","value": false  },
				{"display_name":"Neuropathy","name":"neuropathy","value": false  },
				{"display_name":"Incontinence","name":"incontinence","value": false  },
				{"display_name":"Malnutrition","name":"malnutrition","value": false  },
				{"display_name":"CAD","name":"heart_attack","value": false  },
				{"display_name":"Prior skin pressure injury","name":"prior_skin_pressure_injury","value": false  },
				{"display_name":"Skin Flap / Graft","name":"skin_flap_graft","value": false  },
				{"display_name":"Hip/femur fracture","name":"hip_pelvic_fracture","value": false  },
				{"display_name":"Pelvic fracture","name":"femur_fracture","value": false  },
				{"display_name":"Hypertension","name":"hypertension","value": false  },
				{"display_name":"Respiratory Failure","name":"respiratory_failure","value": false  },
				{"display_name":"Malignancy","name":"malignancy","value": false  },
				{"display_name":"Other","name":"other","value": true }
			],

			past_diagnosis: [
				{"display_name":"Diabetes","name":"diabetes","value": false  },
				{"display_name":"Heart Disease","name":"heart_disease","value": false  },
				{"display_name":"Stroke","name":"stroke","value": false  },
				{"display_name":"Immobility (stroke, paraplegic, quadriplegic)","name":"immobility","value": false  },
				{"display_name":"PVD (peripheral vascular disease)","name":"pvd","value": false  },
				{"display_name":"Neuropathy","name":"neuropathy","value": false  },
				{"display_name":"Incontinence","name":"incontinence","value": false  },
				{"display_name":"Malnutrition","name":"malnutrition","value": false  },
				{"display_name":"CAD","name":"heart_attack","value": false  },
				{"display_name":"Prior skin pressure injury","name":"prior_skin_pressure_injury","value": false  },
				{"display_name":"Skin Flap / Graft","name":"skin_flap_graft","value": false  },
				{"display_name":"Hip/femur fracture","name":"hip_pelvic_fracture","value": false  },
				{"display_name":"Pelvic fracture","name":"femur_fracture","value": false  },
				{"display_name":"Hypertension","name":"hypertension","value": false  },
				{"display_name":"Respiratory Failure","name":"respiratory_failure","value": false  },
				{"display_name":"Malignancy","name":"malignancy","value": false  },
				{"display_name":"Other","name":"other","value": false }
			],
			available_unit_floors: [],
			hide_optional_fields: false,
		};
	},

	onSubmit: function(event) {
		event.preventDefault();
		var self = this;
		var url = "/api/"+config.APIVersion+"/patients";
		self.setState({
		});
		var method = 'PUT'; //for an existing patient
		if(self.props.new_patient) {
			method = 'POST'; //for a new patient
		}

		var json_out = {};
		json_out = this.state;
		delete json_out.existing;

		var mrn = this.state.medical_record_number;
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
			if(data) {
				$.navigate(config.baseUrl+"/patient/edit/"+data.medical_record_number);
			}
			Materialize.toast('Patient successfully updated', 4000, 'rounded');

			//send outcome refresh event
			$(document).trigger("refresh-outcome");
		});
	},

	doInit: function(event) {
		var self = this;
		//populate the unit_floors first
		var url = "/api/"+config.APIVersion+"/admin";
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
				available_unit_floors: JSON.parse(data.unit_floor),
			})
		});

		if(typeof this.props.medical_record_number !== "undefined") {
			//do ajax call to get all user stuffs
			var url = "/api/"+config.APIVersion+"/patients?medical_record_number="+this.props.medical_record_number;
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
				//alert(data.patients[0]['last_name']);
				self.setState({
					existing: true,
					pa_id: data.patients[0]['medical_record_number'],
					name: data.patients[0]['name'],
					last_name: data.patients[0]['last_name'],
					gender: data.patients[0]['gender'],
					DOB: data.patients[0]['DOB'],
					units: data.patients['units'],
					date_of_admission: data.patients[0]['date_of_admission'],
					unit_floor: data.patients[0]['unit_floor'],
					bed_type: data.patients[0]['bed_type'],
					ethnicity: data.patients[0]['ethnicity'],
					braden_score: data.patients[0]['braden_score'],
					mobility: data.patients[0]['mobility'],
					diagnosis: data.patients[0]['diagnosis'],
					past_diagnosis: data.patients[0]['past_diagnosis'],
					medication: data.patients[0]['medication'],
					weight: data.patients[0]['weight'],
					height: data.patients[0]['height'],
					albumin_level: data.patients[0]['albumin_level'],
					A1C: data.patients[0]['A1C'],
					hemoglobin: data.patients[0]['hemoglobin'],
					o2_saturation: data.patients[0]['o2_saturation'],
					blood_pressure: data.patients[0]['blood_pressure'],
					room: data.patients[0]['room'],
				});
				$.setup_pickadate(self);
				var short_mrn = self.state.pa_id.toString().toLowerCase().substr(self.state.pa_id.length - 5).replace(" ", "-");
				$("#patient_page_patient_name").html(self.state.name + ' ' + self.state.last_name);
				$("#patient_page_patient_mrn").html("( "+short_mrn+" )");
			});
		}
	},

	onChange: function(e, ee) {
		var x = $(e.target).attr('id');
		if($(e.target).is(':checkbox')) {
			if(!x.indexOf("past_diagnosis_")) {
				var index = $(e.target).attr("data-past_diagnosis_index");
				this.state.past_diagnosis[index].value = $(e.target).prop("checked");
			}
			else if(!x.indexOf("diagnosis_")) {
				var index = $(e.target).attr("data-diagnosis_index");
				this.state.diagnosis[index].value = $(e.target).prop("checked");
			}
			else if(!x.indexOf("medication_")) {
				var index = $(e.target).attr("data-medication_index");
				this.state.medication[index].value = $(e.target).prop("checked");
			}
			else if(x === "hide_optional_fields") {
				this.state.hide_optional_fields = $(e.target).prop("checked");
			}
			else {
				this.state[x] = $(e.target).prop("checked");
			}
		}
		else {
			this.state[x] = e.target.value;
		}
		this.setState(this.state);

		// none medication control
		var is_med_none = true;
		var none_med_index = -1;
		for(var i=0; i<this.state.medication.length; i++) {
			if(this.state.medication[i].value == true && this.state.medication[i].name != "none") {
				is_med_none = false;
			}
			if(this.state.medication[i].name == "none") {
				none_med_index = i;
			}
		}
		if(is_med_none) {
			this.state.medication[none_med_index].value = true;
		}
		else {
			this.state.medication[none_med_index].value = false;
		}

		// other diagnosis control
		var is_diag_other = true;
		var other_diag_index = -1;
		for(var i=0; i<this.state.diagnosis.length; i++) {
			if(this.state.diagnosis[i].value == true && this.state.diagnosis[i].name != "other") {
				is_diag_other = false;
			}
			if(this.state.diagnosis[i].name == "other") {
				other_diag_index = i;
			}
		}
		if(is_diag_other) {
			this.state.diagnosis[other_diag_index].value = true;
		}

		// other past diagnosis control, maybe not needed
		/*
		var is_past_diag_other = true;
		var other_past_diag_index = -1;
		for(var i=0; i<this.state.past_diagnosis.length; i++) {
			if(this.state.past_diagnosis[i].value == true && this.state.past_diagnosis[i].name != "other") {
				is_past_diag_other = false;
			}
			if(this.state.past_diagnosis[i].name == "other") {
				other_past_diag_index = i;
			}
		}
		if(is_past_diag_other) {
			this.state.past_diagnosis[other_past_diag_index].value = true;
		}
		*/

		$('#patient-form select').material_select();
	},

	componentDidUpdate: function() {
		var edit = this.props.edit;
		$('#patient-form :input').each(function(){
			var v = $(this);
			if(!edit) {
				v.prop('disabled', true);
			}
			else {
				v.prop('disabled', false);
			}
		});
		//needed for materialize to render the select forms
		$('#patient-form select').material_select();
		// for HTML5 "required" attribute
		$("#patient-form select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
	},

	componentDidMount: function() {
		this.doInit();
		var edit = this.props.edit;
		$('#patient-form :input').each(function(){
			var v = $(this);
			if(!edit) {
				v.prop('disabled', true);
			}
			else {
				v.prop('disabled', false);
			}
		});
		//needed for materialize to render the select forms
		$('#patient-form select').material_select();
		$('#patient-form select').on('change', this.onChange);
		// for HTML5 "required" attribute
		$("#patient-form select[required]").css({display: "inline", height: 0, padding: 0, width: 0});
		$("#patient-form").on('submit', this.onSubmit);
		if(this.props.new_patient) {
			$.setup_pickadate(this);
		}
	},

	render: function() {

		var self = this;

		var submit_text = "Add patient";
		if(this.state.medical_record_number) {
			submit_text = "Update patient";
		}

		var edit_button;
		if(!this.props.edit) {
			edit_button = <div className="top-right-button">
				<a className="btn-floating btn-large waves-effect waves-light orange" href={config.baseUrl+"/patient/edit/"+this.props.medical_record_number}><i className="material-icons">mode_edit</i></a>
				<span>Edit patient</span>
			</div>
		}

		var optional_fields_checkbox = <div className="col l6 m6 s12">
					<input type="checkbox" id="hide_optional_fields" name="hide_optional_fields" checked={self.state.hide_optional_fields} onChange={self.onChange}/>
					<label htmlFor="hide_optional_fields">Hide Optional Fields</label>
			</div>;

		var diagnosis_inputs = this.state.diagnosis.map(function(diagnosis, index){
			return <div className="col l6 m6 s12"  key={diagnosis+"_"+index}>
				<p>
					<input type="checkbox" id={"diagnosis_"+self.state.diagnosis[index].name} name={"diagnosis_"+self.state.diagnosis[index].name} checked={self.state.diagnosis[index].value} onChange={self.onChange} data-diagnosis_index={index}/>
					<label htmlFor={"diagnosis_"+diagnosis.name}>{diagnosis.display_name}</label>
				</p>
			</div>
		});

		var past_diagnosis_inputs = this.state.past_diagnosis.map(function(diagnosis, index){
			return <div className="col l6 m6 s12"  key={diagnosis+"_past_"+index}>
				<p>
					<input type="checkbox" id={"past_diagnosis_"+self.state.past_diagnosis[index].name} name={"past_diagnosis_"+self.state.past_diagnosis[index].name} checked={self.state.past_diagnosis[index].value} onChange={self.onChange} data-past_diagnosis_index={index}/>
					<label htmlFor={"past_diagnosis_"+diagnosis.name}>{diagnosis.display_name}</label>
				</p>
			</div>
		});

		var medication_inputs = this.state.medication.map(function(medication, index){
			return <div className="col l4 m6 s12" key={medication+"_"+index}>
					<p >
						<input type="checkbox" id={"medication_"+self.state.medication[index].name} name={"medication_"+self.state.medication[index].name} checked={self.state.medication[index].value} onChange={self.onChange} data-medication_index={index}/>
						<label htmlFor={"medication_"+medication.name}>{medication.display_name}</label>
					</p>
			</div>
		});

		var unit_floor_select = this.state.available_unit_floors.map(function(u_name, index){
			return <option key={index+"-"+u_name} value={u_name}>{u_name}</option>
		});

		var hide_fields = "";
		if (this.state.hide_optional_fields != null && this.state.hide_optional_fields != undefined && this.state.hide_optional_fields){
			hide_fields = " hide";
		}
		else {
			hide_fields = "";
		}

		return (
			<section className="new-patient">

				{edit_button}
				<div style={{display: "block", float: "right"}}><span className="red-text"> * </span> = Required Field</div>
				<div className="row">
					<form className="col s12" id="patient-form">

						<div className="row">
							<div className="input-field col l6 m6 s6">
								<input name="name" id="name" type="text" className="validate" value={this.state.name} onChange={this.onChange} required/>
								<label htmlFor="name" className={ (this.state.name) ? "active" : null}>Patient First Name<span className="red-text"> *</span></label>
							</div>
							<div className="input-field col l6 m6 s6">
								<input name="last_name" id="last_name" type="text" className="validate" value={this.state.last_name} onChange={this.onChange} required/>
								<label htmlFor="last_name" className={ (this.state.last_name) ? "active" : null}>Patient Last Name<span className="red-text"> *</span></label>
							</div>
							<div>
								{optional_fields_checkbox}
							</div>
						</div>
						<input name="medical_record_number" id="medical_record_number" type="hidden" value={this.state.medical_record_number} required/>

						<div className="row">
							<div className="input-field col l2 push-l10 m2 push-m10 s12">
								<select name="units" id="units" value={this.state.units} defaultValue={this.state.units} onChange={this.onChange} required>
									{/*<option value="">Choose measurement units</option>*/}
									<option value="english">Imperial/English</option>
									<option value="metric">Metric</option>
									{/*<option value=""disabled></option>*/}
								</select>
								<label>Units<span className="red-text"> *</span></label>
							</div>
							<div className="input-field col l4 pull-l2 m4 pull-m2 s12">
								<select name="unit_floor" id="unit_floor" value={this.state.unit_floor} required>
									<option value="">Choose unit/floor</option>
									{unit_floor_select}
								</select>
								<label>Unit/Floor<span className="red-text"> *</span></label>
							</div>
							<div className="input-field col l4 pull-l2 m4 pull-m2 s12">
								<input name="room" id="room" type="text" className="validate" value={this.state.room} onChange={this.onChange} required/>
								<label htmlFor="room" className={ (this.state.room) ? "active" : null}>Room Number<span className="red-text"> *</span></label>
							</div>
						</div>

						<div className="row">
							<div className="input-field col l4 m4 s12">
								<input name="date_of_admission" id="date_of_admission" className="datepicker" type="date" value={this.state.date_of_admission} onChange={this.onChange} required/>
								<label htmlFor="date_of_admission" className="active">Date of Admission<span className="red-text"> *</span></label>
							</div>
						</div>

						<div className="row">
							<div className="input-field col l4 m4 s12">
								<input name="DOB" id="DOB" type="date" value={this.state.DOB} onChange={this.onChange} required/>
								<label htmlFor="DOB" className="active">Date of Birth<span className="red-text"> *</span></label>
							</div>
							<div className="input-field col l4 m4 s12">
								<select name="gender" id="gender" value={this.state.gender} onChange={this.onChange} required>
									<option value="">Choose patient gender</option>
									<option value="female">Female</option>
									<option value="male">Male</option>
								</select>
								<label>Gender<span className="red-text"> *</span></label>
							</div>
							<div className="optional_input_field" className={"input-field col l4 m4 s12 "+hide_fields}>
								<select name="ethnicity" id="ethnicity" value={this.state.ethnicity} defaultValue={this.state.ethnicity}>
									<option value="">Choose patient ethnicity</option>
									<option value="african_american">African American</option>
									<option value="asian">Asian</option>
									<option value="caucasion">Caucasian</option>
									<option value="hispanic">Hispanic</option>
									<option value="other">Other</option>
								</select>
								<label>Ethnicity</label>
							</div>
						</div>

						<div className="row">
							<div className="input-field col l4 m4 s12">
								<select name="braden_score" id="braden_score" value={this.state.braden_score} defaultValue={this.state.braden_score} required>
									<option value="">Choose patient Braden score</option>
									<option value="na">Not Applicable</option>
									<option value="severe">Severe 9</option>
									<option value="high">High 10-12</option>
									<option value="moderate">Moderate 13-14</option>
									<option value="mild">Mild 15-18</option>
								</select>
								<label>Braden score<span className="red-text"> *</span></label>
							</div>
						</div>

						<div className="row">
							<div className="input-field col l4 m4 s12">
								<select name="mobility" id="mobility" value={this.state.mobility} defaultValue={this.state.mobility} required>
									<option value="">Choose patient mobility</option>
									<option value="independent">Independent</option>
									<option value="1_person_assist">1 Person Assist</option>
									<option value="2_person_assist">2 Person Assist</option>
									<option value="total_dependent">Total Dependent</option>
								</select>
								<label>Mobility<span className="red-text"> *</span></label>
							</div>
						</div>
						<div id="optional_fields" className={"optional_input_field "+hide_fields}>
							<div className="row">
								<div className="input-field col l4 m4 s12">
									<select name="bed_type" id="bed_type" value={this.state.bed_type}>
										<option value="">Choose patient bed type</option>
										<option value="foam_gel">Foam/Gel</option>
										<option value="low_airloss">Low Airloss</option>
										<option value="alternating_pressure">Alternating Pressure Mattress</option>
										<option value="waffle_style">Waffle style mattress cover</option>
										<option value="rotating_bed">Rotating bed</option>
										<option value="other">Other</option>
									</select>
									<label>Bed Types</label>
								</div>
							</div>
							<div className="row">
								<div className="col l6 m6 s6 patient-checkbox-list">
									Diagnosis:
									<div>
										{diagnosis_inputs}
									</div>
								</div>
								<div className="col l6 m6 s6 patient-checkbox-list">
									Past Diagnosis:
									<div>
										{past_diagnosis_inputs}
									</div>
								</div>
							</div>

							<div className="row">
								<div className="col s12 patient-checkbox-list">
									Medication:
									<div>
										{medication_inputs}
									</div>
								</div>
							</div>

							<div className="row">
								<div className="input-field col l4 m4 s12" >
									<input name="weight" id="weight" type="number" step="any" className="validate" value={this.state.weight} onChange={this.onChange}/>
									<label htmlFor="weight" className={ (this.state.weight) ? "active" : null}>Weight ({this.state.units})</label>
								</div>
							</div>

							<div className="row">
								<div className="input-field col l4 m4 s12" >
									<input name="height" id="height" type="number" step="any" className="validate" value={this.state.height} onChange={this.onChange}/>
									<label htmlFor="height" className={ (this.state.height) ? "active" : null}>Height ({this.state.units})</label>
								</div>
							</div>

							<div className="row">
								<div className="input-field col l4 m4 s12" >
									<input name="albumin_level" id="albumin_level" type="text" className="validate" value={this.state.albumin_level} onChange={this.onChange} />
									<label htmlFor="albumin_level" className={ (this.state.albumin_level) ? "active" : null}>Albumin Level</label>
								</div>
							</div>

							<div className="row">
								<div className="input-field col l4 m4 s12" >
									<input name="A1C" id="A1C" type="text" className="validate" value={this.state.A1C} onChange={this.onChange} />
									<label htmlFor="A1C" className={ (this.state.A1C) ? "active" : null}>A1C</label>
								</div>
							</div>

							<div className="row">
								<div className="input-field col l4 m4 s12" >
									<input name="hemoglobin" id="hemoglobin" type="text" className="validate" value={this.state.hemoglobin} onChange={this.onChange}/>
									<label htmlFor="hemoglobin" className={ (this.state.hemoglobin) ? "active" : null}>Hemoglobin</label>
								</div>
							</div>

							<div className="row">
								<div className="input-field col l4 m4 s12" >
									<input name="o2_saturation" id="o2_saturation" type="text" className="validate" onChange={this.onChange} value={this.state.o2_saturation} defaultValue={this.state.o2_saturation} />
									<label htmlFor="o2_saturation" className={ (this.state.o2_saturation) ? "active" : null}>O2 Saturation</label>
								</div>
							</div>

							<div className="row">
								<div className="input-field col l4 m4 s12" >
									<input name="blood_pressure" id="blood_pressure" type="text" className="validate" value={this.state.blood_pressure} onChange={this.onChange}/>
									<label htmlFor="blood_pressure" className={ (this.state.blood_pressure) ? "active" : null}>Blood Pressure</label>
								</div>
							</div>
						</div>

						<div className="row">
							<button id="patient-submit" className="btn waves-effect waves-light" type="submit" name="action">{submit_text}
								<i className="material-icons right">assignment_ind</i>
							</button>
						</div>
					</form>
				</div>

			</section>
		);
	}
});

export default PatientForm;

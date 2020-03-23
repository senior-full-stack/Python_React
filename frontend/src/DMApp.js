import React from 'react'; //, { Component } from 'react';

import Footer from './Footer';

import Dashboard from './Dashboard';

import Users from './Users';
import {UserForm, UserPasswordForm} from './UserForm';

import AdminSettings from './AdminSettings';

import Patients from './Patients';
import PatientPage from './PatientPage';
import PatientForm from './PatientForm';
import PatientOutcome from './PatientOutcome';
import EventsTimeline from './EventsTimeline';

import {PatientInfoReport, PUStatusReport, EventsReport, RepositionReport, AlarmResponseReport} from './Reports';

import Devices from './Devices';
import DevicePage from './DevicePage';
import DeviceForm from './DeviceForm';

import {Alerts} from './Alerts'; //, DashboardAlerts

import Config from './Config';

import 'materialize-css';

import logo from './img/pa_logo.png';

var config = new Config();

var $ = window.jQuery = require('jquery');

var RouterMixin = require('react-mini-router').RouterMixin,
  navigate = require('react-mini-router').navigate;

$.navigate = navigate;

$.setup_pickadate = function(component) {
  // cache this so we can reference it inside the datepicker
  //var self = this;
  // the element
  $.each(component.dates, function(i, date_ref) {
    $(date_ref).pickadate({
      format: 'yyyy-mm-dd',
      formatSubmit: 'yyyy-mm-dd',
      selectMonths: true,
      selectYears: 150,
      max: new Date(),
      closeOnSelect: true,
      onStart: function(e) {
        this.set('select', component.state[$(this.$node[0]).attr('id')]);
      },
      onClose: function() {
        // you can use any of the pickadate options here
        var val = this.get('select', 'yyyy-mm-dd');
        component.state[$(this.$node[0]).attr('id')] = val;
        component.setState(component.state);
        if(component.onDateChange) {
          component.onDateChange();
        }
        $(document.activeElement).blur();
      },
    });
  });
};

var current_menu_item = "";

/* UTILITIES */
/*function checkLogin() {
  if(sessionStorage["token"] && sessionStorage["token"] != "") {
    return true;
  }
  return false;
}*/

$(document).on("new_tab_active", function(e, ee){
  //console.log("got tab active event! "+JSON.stringify(ee))
});

//if we get a 401 from any request for not being logged in, send user here to log in
function failToLogin() {
  window.location.href = config.baseUrl+"/login";
}

var menu_items = {
    "dashboard" : {name: "Dashboard", url: "/dashboard", active: false, mobile: true},
//    "units" : {name: "Units", url: "/units", active: false},
    "patients" : {name: "Patients", url: "/patients", active: false, mobile: true},
    "users": {name: "Users", url: "/users", active: false, mobile: true},
    "devices": {name: "Devices", url: "/devices", active: false, mobile: true},
    "reports": {name: "Reports", url: "/reports", active: false, mobile: true},
    "alerts": {name: "Alerts", url: "/alerts", active: false, mobile: true},
    "my_account" : {name: "My account", url: "/my-account", active: false, mobile: true},
    "admin" : {name: "Admin settings", url: "/admin", active: false, mobile: true},
    "signout": {name: "Sign Out", url: "/logout", active: false, mobile: true},
};

var badges = new Array();

function menu_activate(item) {
    current_menu_item = item;
}

var Nav = React.createClass({
  getInitialState: function() {
    return {
      badges: [],
      menu: Object.keys(menu_items).map(function(val, index){
          var menu_item = menu_items[val];
          if(menu_item.active == true) {
            menu_item.active = "active"
          }
        if(menu_item.name=="Admin settings") {
          return
        }
        return (<li key={val} className={menu_item.active}><a href={config.baseUrl+menu_item.url}>{menu_item.name}</a></li>);
      })
    }
  },

  render: function() {
    var hidden = "";
    var self = this;
    if(this.props.hide == true) {
      hidden = "hide";
    }

    for (var key in menu_items) {
      menu_items[key].active = false;
    }
    if(current_menu_item) {
      menu_items[current_menu_item].active = true;
    }

    var new_menu = Object.keys(menu_items).map(function(val, index){
      var menu_item = menu_items[val];
      if(menu_item.active == true) {
        menu_item.active = "active"
      }
      if(menu_item.name=="Admin settings" && (!self.props.current_user || self.props.current_user.role != "admin")) {
        return;
      }
      return (<li key={val} className={menu_item.active}><a href={config.baseUrl+menu_item.url}>{menu_item.name}{self.state.badges[menu_item.name]}</a></li>);
    });
    var new_menu_mobile = Object.keys(menu_items).map(function(val, index){
      var menu_item = menu_items[val];
      if(menu_item.active == true) {
        menu_item.active = "active"
      }
      if(menu_item.name=="Admin settings" && (!self.props.current_user || self.props.current_user.role != "admin")) {
        return;
      }
      if(!menu_item.mobile) {
        return;
      }
      return (<li key={val} className={menu_item.active}><a href={config.baseUrl+menu_item.url}>{menu_item.name}{self.state.badges[menu_item.name]}</a></li>);
    });

    return (
    <nav className={"light-blue  lighten-2 "+hidden} role="navigation" id="navigation">
      <div className="nav-wrapper container">
        <span id="logo-container" href="#" className="brand-logo"><a href={config.baseUrl+"/dashboard"}><img id="logo-img" src={logo}></img></a></span>
        <ul id="desktop-nav" className="right hide-on-med-and-down">
          {new_menu}
        </ul>
        {/* fixed class would go below to have always shown on large desktop*/}
        <ul id="nav-mobile" className="side-nav">
          {new_menu_mobile}
        </ul>
        <a href="#" data-activates="nav-mobile" className="button-collapse"><i className="material-icons">menu</i></a>
      </div>
    </nav>
    );
  }
});



var DMApp = React.createClass({

  mixins: [RouterMixin],

  routes: {
    '/': 'dashboard',
    '/dashboard': 'dashboard',
    '/my-account': 'my_account',
    '/my-account/change-password': 'change_my_password',
    '/admin': 'admin_settings',
    '/users': 'users',
    '/user/new': 'new_user',
    '/users/edit/:email': 'edit_user',
    '/units': 'units',
    '/patients': 'patients',
    '/patient/edit/:mrn': 'edit_patient',
    '/patient/new': 'new_patient',
    '/patient/:mrn': 'view_patient',
    '/patient/timeline/:mrn': 'view_patient_timeline',
    '/patient/reports/:mrn': 'view_patient_info_report',
    '/patient/reports/info/:mrn': 'view_patient_info_report',
    '/patient/reports/pu/:mrn': 'view_patient_pu_report',
    '/patient/reports/events/:mrn': 'view_patient_events_report',
    '/patient/reports/reposition/:mrn': 'view_patient_reposition_report',
    '/patient/reports/alarm_response/:mrn': 'view_patient_alarm_response_report',
    '/patient/outcome/:mrn': 'patient_outcome',
    '/alerts': 'alerts',
    '/devices': 'devices',
    '/devices/defaults': 'devices_defaults',
    '/devices/:device_id': 'view_device',
    '/reports': 'patients_info_reports',
    '/reports/info': 'patients_info_reports',
    '/reports/pu': 'patients_pu_reports',
    '/reports/events': 'patients_events_reports',
    '/reports/reposition': 'patients_reposition_reports',
    '/reports/alarm_response': 'patients_alarm_response_reports',
    '/logout': 'logout'
  },
  notifyAlerts: function(p_id) {
	  var name_or_id = "A patient";
		if (p_id != undefined) {
			name_or_id = p_id + ",";
		}
	  if (!Notification) {
	    alert('Notifications are not available on this system');
	    return;
	  }

	  if (Notification.permission !== "granted")
	    Notification.requestPermission();
	  else {
	    var notification = new Notification('Patient Pressure Alert!', {
				icon: logo,
	      body: name_or_id + " requires attention",
	    });
	    notification.onclick = function () {
	      parent.focus();
	      window.focus();
	      this.close();
	    };
	  }
	},

  checkAlerts: function(event) {
		var self = this;
		var red_alerts = [];
		var yellow_alerts = [];
		var yellow_bordered_alerts = [];
		var orange_alerts = [];
		var orange_bordered_alerts = [];
		var green_alerts = [];
		var sensor_stopped_alerts = [];
		var grey_alerts = [];
		var device_unplugged_alerts = [];
		var facility_locations = {};

		var url = config.baseHost +"/api/"+config.APIVersion+"/status-station";
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
				if(self.state.facility_location_filter && self.state.facility_location_filter && self.state.facility_location_filter != "all" && self.state.facility_location_filter != bli.unit_floor) {
					continue;
				}
				for(ii=0; ii<bli.events.length; ii++) {
					var evtt = bli.events[ii];
					if(evtt != 'undefined' && evtt.message.toLowerCase().indexOf('alarm') > -1)	{
					  			console.log('hui3');

						self.notifyAlerts();
					}
				}
			}
		});
	},

  acceptedEULA: function() {
    var tmpu = this.state.current_user;
    tmpu.eula_accepted = true;
    this.setState({current_user: tmpu});
    var url = config.baseHost+"/api/"+config.APIVersion+"/users/"+this.state.current_user.email;
    $.ajax(
        {
          url: url,
          contentType: 'application/json; charset=UTF-8',
          dataType: 'json',
          data: JSON.stringify(this.state.current_user),
          method: 'PUT',
          beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+sessionStorage['token']);},
          statusCode: {
            401: function() {
              navigate(config.baseUrl+"/logout");
            }
          },
        }).done(function(data){
    });
  },

  declinedEULA: function() {
    navigate(config.baseUrl+"/logout");
  },

  componentDidMount: function() {
    var self = this;
    $('.button-collapse').sideNav();

    $("#main-container").css("minHeight", ($(window).height() - 128 - 58)+"px");

    $.fn.extend({
      qcss: function(css) {
        return $(this).queue(function(next) {
          $(this).css(css);
          next();
        });
      },
      qclass: function(new_class) {
        return $(this).queue(function(next) {
          $(this).removeClass();
          $(this).addClass(new_class);
          next();
        });
      }
    });

    $("#tos-link").click(function() {
      $('#tos-modal').modal();
      $('#tos-modal').modal('open');
    });
  },

  componentWillMount: function() {
    var self = this;

    var url = config.baseHost +"/api/"+config.APIVersion+"/users/current";
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
          self.setState({current_user: data});
          setInterval(self.checkAlerts, 7000);
          if(!self.state.current_user.eula_accepted) {
            $('#eula-modal').modal({dismissible: false});
            $("#eula_agree").click(self.acceptedEULA);
            $("#eula_decline").click(self.declinedEULA);
            $('#eula-modal').modal('open');
          }
          self.forceUpdate();
        });

    url = "/xajax/eula.txt";
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
          $("#eula-modal-text").html(data);
        });

    url = "/xajax/tos.txt";
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
          $("#tos-modal-text").html(data);
        });
  },

  render: function() {
    var current_route = this.renderCurrentRoute();
    $('.button-collapse').sideNav('hide');
    return (
      <div id="app_react">
        <Nav current_user={this.state.current_user}/>

        <div className="container" id="main-container">
          <section id="main-app">{current_route}</section>
        </div>
        <Footer />
      </div>
              );
  },

  dashboard: function() {
    menu_activate("dashboard");
    return <Dashboard current_user={this.state.current_user}/>;
  },

  my_account: function() {
    menu_activate("my_account");
    return <UserForm user_email={this.state.current_user.email} current_user={this.state.current_user} />;
  },

  admin_settings: function() {
    menu_activate("admin");
    return <AdminSettings current_user={this.state.current_user} />;
  },

  edit_user: function(email) {
    menu_activate("users");
    return <UserForm user_email={email}  current_user={this.state.current_user} />;
  },

  change_password: function(email) {
    menu_activate("my_account");
    return <UserPasswordForm user_email={email} />;
  },

  change_my_password: function() {
    menu_activate("my_account");
    return <UserPasswordForm user_email={this.state.current_user.email} />;
  },

  units: function() {
    menu_activate("units");
    return <div>UNITS</div>;
  },

  /*  PATIENTS  */

  patients: function() {
    menu_activate("patients");
    return <Patients current_user={this.state.current_user}/>;
  },

  new_patient: function() {
    menu_activate("patients");
    return <PatientForm edit={true} new_patient={true}/>;
  },

  view_patient: function(mrn) {
    menu_activate("patients");

    return <PatientPage medical_record_number={mrn} edit={false}/>;
  },

  view_patient_timeline: function(mrn) {
    menu_activate("patients");

    return <EventsTimeline medical_record_number={mrn}/>;
  },

  view_patient_info_report: function(mrn) {
    menu_activate("patients");
    return <PatientInfoReport medical_record_number={mrn}/>;
  },

  view_patient_pu_report: function(mrn) {
    menu_activate("patients");
    return <PUStatusReport medical_record_number={mrn}/>;
  },

  view_patient_events_report: function(mrn) {
    menu_activate("patients");
    return <EventsReport medical_record_number={mrn}/>;
  },

  view_patient_reposition_report: function(mrn) {
    menu_activate("patients");
    return <RepositionReport medical_record_number={mrn}/>;
  },

  view_patient_alarm_response_report: function(mrn) {
    menu_activate("patients");
    return <AlarmResponseReport medical_record_number={mrn}/>;
  },

  patient_outcome: function(mrn) {
    menu_activate("patients");

    return <PatientOutcome medical_record_number={mrn}/>;
  },

  edit_patient: function(mrn) {
    menu_activate("patients");

    return <PatientPage medical_record_number={mrn} edit={true}/>;
  },

  /*  USERS  */

  users: function() {
    menu_activate("users");
    return <Users current_user={this.state.current_user}/>;
  },

  new_user: function() {
    menu_activate("users");
    return <UserForm new_user={true} current_user={this.state.current_user} />;
  },

  devices: function() {
    menu_activate("devices");
    return <Devices current_user={this.state.current_user} />;
  },

  view_device: function(device_id) {
    menu_activate("devices");
    return <DeviceForm device_id={device_id} edit={true} show_title={true} />;
  },

  devices_defaults: function(mrn) {
    menu_activate("devices");

    return <DevicePage medical_record_number="default" device_id="default"/>;
  },

  patients_info_reports: function() {
    menu_activate("reports");
    return <div><PatientInfoReport medical_record_number={null} /></div>;
  },

  patients_events_reports: function() {
    menu_activate("reports");
    return <EventsReport medical_record_number={null} />;
  },

  patients_reposition_reports: function() {
    menu_activate("reports");
    return <RepositionReport medical_record_number={null} />;
  },

  patients_alarm_response_reports: function() {
    menu_activate("reports");
    return <AlarmResponseReport medical_record_number={null} />;
  },

  patients_pu_reports: function() {
    menu_activate("reports");
    return <PUStatusReport medical_record_number={null} />;
  },

  alerts: function() {
    menu_activate("alerts");
    return <Alerts patient_name="Joe X. Patient"/>;
  },

  logout: function() {
    sessionStorage.removeItem("token");
    failToLogin();
  },

  message: function(text) {
    return <div>{text}</div>;
  },

  notFound: function(path) {
    return <div className="not-found">Page Not Found: {path}</div>;
  },

  getInitialState: function() {
    return {
      state: 'login',
      current_user: {
        "name": "",
        "email": "",
        "role": "",
      },
    };
  }

});


export default DMApp;

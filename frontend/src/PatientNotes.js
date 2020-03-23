import React from 'react';
import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');

var moment = require('moment');

var PatientNotes = React.createClass({

	getInitialState: function() {
		return {

		};
	},

	onSUbmit: function(event) {

	},

	render() {
		var delete_note;
		if(this.props) {
			delete_note = <td style={{"border": 1 + "px solid", "textAlign": "center"}}>
				<a className="btn-name waves-light delete-click">
					<i className="material-icons red-text">delete</i>
				</a>
			</td>
		}
		return(
			<div className="notes-editor">
				<label style={{"fontSize": 15 +"px", "color": "black"}}>ADD PATIENT NOTE</label>
				<div style={{"width": 600 + "px"}}>
					<textarea style={{"height": 100 + "px"}} placeholder="Enter Patient Info Here" />
				</div>
				<button id="submit_button" type="submit" className="btn waves-effect waves-light light-blue lighten-2" style={{"marginTop": 10 + "px", "marginBottom": 10 + "px"}} name="action">SAVE NOTE</button>
				<hr />
				<h6 style={{"marginTop": 20 + "px", "marginBottom": 20 + "px"}}>NOTES HISTORY</h6>
				<div>
					<table>
						<thead>
							<tr>
								<th style={{"width": 250 +"px", "textAlign": "center", "padding": 0 + "px"}}>Date</th>
								<th style={{"textAlign": "center", "padding": 0 + "px"}}>Notes</th>
								<th style={{"width": 70 +"px", "textAlign": "center", "padding": 0 + "px"}}>Delete</th>
							</tr>
						</thead>
						<tbody>
							<tr>
								<td style={{"border": 1 + "px solid"}}></td>
								<td style={{"border": 1 + "px solid"}}></td>
								{delete_note}
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		)
	}
});

export default PatientNotes;
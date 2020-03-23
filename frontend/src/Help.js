import React from 'react';
import Config from './Config';

var config = new Config();
var $ = window.jQuery = require('jquery');

var Help = React.createClass({

	render: function() {
	return (
		<div>
			<div style={{'marginTop': 60 + 'px','textAlign': 'center'}}>
				<div style={{'marginBottom': 40 + 'px'}}><h4> User Guide & Product Instructions</h4></div>
				<div style={{'marginBottom': 30 + 'px'}}>
					<p>
						<a href="src/helpArticles/D-1013_PressureAlert Decision Tree_LR.pdf" target="_blank">PressureAlert Decision Tree</a>	
					</p><hr style={{'width': 280 + 'px'}} />
				</div>
				<div style={{'marginBottom': 30 + 'px'}}>
					<p>
						<a href="src/helpArticles/D-1007_PressureAlert Core Team QRG Flyer_LR.pdf" target="_blank">PressureAlert Core Team QRG Flyer</a>
					</p><hr style={{'width': 280 + 'px'}} />
				</div>
				<div style={{'marginBottom': 30 + 'px'}}>
					<p>
						<a href="src/helpArticles/D-1006_PressureAlert Tablet Troubleshooting_LR.pdf" target="_blank">PressureAlert Tablet Troubleshooting</a>
					</p><hr style={{'width': 280 + 'px'}} />
				</div>
			</div>
			<div style={{'marginTop': 60 + 'px','textAlign': 'center'}}>
				<p style={{'fontSize': 20 + 'px', 'fontWeight': 'bold'}}>COULD NOT FIND WHAT YOU NEED IN OUR HELP DOCS?</p>
				<p style={{'fontSize': 20 + 'px', 'fontWeight': 'bold'}}>CONTACT US</p>
				<div style={{'margin': 20 + 'px'}}><a href="mailto: info@digitalhealths.com"><i style={{'fontSize': 25+'px', 'verticalAlign': 'middle', 'position': 'relative', 'top': -1 + 'px'}} className="material-icons">email</i></a><span>info@digitalhealths.com</span></div>
				<div style={{'margin': 20 + 'px'}}><i style={{'fontSize': 25+'px', 'verticalAlign': 'middle', 'position': 'relative', 'top': -1 + 'px'}} className="material-icons">phone</i><span> +1(855)-727-0347</span></div>
			</div>
		</div>
	)
}

});

export default Help;
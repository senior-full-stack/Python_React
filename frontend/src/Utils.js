
var BatteryUtils =  {};
BatteryUtils.battery_percentage = function(adc_reading) {
	var battery_full = 2980; // in millivolts
	var battery_dead = 2400; // in millivolts

	var bat_color = "green-text";
	var bat_text = "100%";
	if(adc_reading == 0) {
		var bat_color = "";
		var bat_text = "Not Available"
	}
	else if(adc_reading < 2860 && adc_reading > 2700) {
		var bat_color = "green-text";
		var bat_text = "80%";
	}
	else if(adc_reading <= 2700 && adc_reading > 2600) {
		var bat_color = "orange-text";
		var bat_text = "50%";
	}
	else if(adc_reading <= 2600 && adc_reading > 2500) {
		var bat_color = "orange-text";
		var bat_text = "20%";
	}
	else if(adc_reading <= 2500) {
		var bat_color = "red-text";
		var bat_text = "5%";
	}
	return {color: bat_color, text: bat_text};
};

var DateUtils = {};
DateUtils.to_utc_date = function(local_date) {
	var ldate = new Date(moment(local_date + " 00:00:00", "YYYY-MM-DD HH:mm:ss"));
	var utcdate = ldate.getUTCFullYear()+"-"+(ldate.getUTCMonth()+1)+"-"+ldate.getUTCDate()+" "+ldate.getUTCHours()+":"+ldate.getUTCMinutes();
	return utcdate;
};

export { BatteryUtils, DateUtils };

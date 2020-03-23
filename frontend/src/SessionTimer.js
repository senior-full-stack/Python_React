import React, { Component } from "react";
import DMApp from "./DMApp";
import Login from "./Login";
import Config from "./Config";
import IdleTimer from "react-idle-timer";
import swal from "sweetalert";
import Dashboard from "./Dashboard";
import { logout } from "./DMApp";

var APP = {};
var baseHost = Config.baseHost;
var baseUrl = Config.baseUrl;
var APIVersion = Config.APIVersion;

var RouterMixin = require("react-mini-router").RouterMixin,
  navigate = require("react-mini-router").navigate;

$.navigate = navigate;

var config = new Config();

/* CONFIG STUFF UP HERE */

String.prototype.capitalizeFirstLetter = function() {
  return this.charAt(0).toUpperCase() + this.slice(1);
};

//fix for IE11 which doesn't support endswith
if (typeof String.prototype.endsWith !== "function") {
  String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
  };
}

class App extends Component {
  constructor(props, context) {
    super(props, context);
    console.log("props: ", this.props);
    App.contextTypes = {
      router: React.PropTypes.func.isRequired
    };
    this.state = {
      timeout: 840000,
      showModal: false,
      userLoggedIn: false,
      isTimedOut: false
    };

    this.idleTimer = null;
    this.onAction = this._onAction.bind(this);
    this.onActive = this._onActive.bind(this);
    this.onIdle = this._onIdle.bind(this);
  }

  _onAction(e) {
    console.log("user did something", e);
    this.setState({ isTimedOut: false });
  }

  _onActive(e) {
    console.log("user is active", e);
    this.setState({ isTimedOut: false });
  }

  _onIdle(e) {
    console.log("user is idle", e);
    const isTimedOut = this.state.isTimedOut;
    if (isTimedOut) {
      setTimeout(() => {
        logout;
        navigate(config.baseUrl + "/logout");
      }, 900000);
    } else {
      this.setState({ showModal: true });
      this.idleTimer.reset();
      this.setState({ isTimedOut: true });
    }
    swal({
      title: "Your session is about to expire.",
      text: "You will be logged out in 60 seconds.",
      closeOnClickOutside: false,
      closeOnEsc: false,
      icon: "warning",
      buttons: true,
      content: () => Swal.getTimerLeft(),
      buttons: ["Continue Session", "Logout"],
      dangerMode: true
    }).then((Session) => {
      if (Session) {
        logout;
        navigate(config.baseUrl + "/logout");
        swal("logged Out", {
          icon: "success"
        });
      } else {
      }
    });
  }

  render() {
    if (sessionStorage["token"] && sessionStorage["token"] !== "") {
      return (
        <div>
          <IdleTimer
            ref={(ref) => {
              this.idleTimer = ref;
            }}
            element={document}
            onActive={this.onActive}
            onIdle={this.onIdle}
            onAction={this.onAction}
            debounce={250}
            timeout={this.state.timeout}
          />
          <DMApp history="true" root={baseUrl} />
        </div>
      );
    }
    return (
      <div>
        <Login />
      </div>
    );
  }
}
export default App;

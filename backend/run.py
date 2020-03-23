from dm_app.app import app as application
from werkzeug.serving import WSGIRequestHandler
WSGIRequestHandler.protocol_version = "HTTP/1.1"
application.run(debug=True, host='0.0.0.0', port=5666)

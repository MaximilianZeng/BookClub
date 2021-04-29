# Gevent needed for sockets
from gevent import monkey
# import resource
monkey.patch_all()

# Imports
import os
from flask import Flask, render_template
from flask_socketio import SocketIO

# custom imports
import data_loaders

# Configure app
socketio = SocketIO()
app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])

# load read-only data
# print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (2**20))
app.data = data_loaders.load_data()
# print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (2**20))

# Import + Register Blueprints
from app.irsystem import irsystem as irsystem
app.register_blueprint(irsystem)

# Initialize app w/SocketIO
socketio.init_app(app)

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template("404.html"), 404

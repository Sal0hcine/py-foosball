from gevent import monkey
monkey.patch_all()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask.ext.cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config.from_object('config')
db = SQLAlchemy(app)
socketio = SocketIO(app)

from app import views



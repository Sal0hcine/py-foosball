#!foosball/bin/python
from app import app, socketio
# app.run(debug=True)
socketio.run(app, "0.0.0.0", 5000)
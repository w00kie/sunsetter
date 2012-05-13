import os
import json
import math
import datetime

import sunazymuth

from flask import Flask
from flask import request
from flask import render_template
app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')
	
@app.route('/getEphemerides', methods=['POST'])
def getEphemerides():
	lat = float(request.form['lat'])
	return json.dumps(sunazymuth.GetEphemerides(lat))

@app.route('/findMatch', methods=['POST'])
def findMatch():
	lat = float(request.form['lat'])
	az = float(request.form['az'])
	fullyear = sunazymuth.GetEphemerides(lat)
	return json.dumps(sunazymuth.GetMatchingDay(fullyear,az))

if __name__ == '__main__':
	#Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	debug = os.environ.get('DEBUG', True)
	app.run(host='0.0.0.0', port=port, debug=debug)
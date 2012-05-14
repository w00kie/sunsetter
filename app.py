import os
import json
import pylibmc

import sunazymuth

from flask import Flask
from flask import request
from flask import render_template
app = Flask(__name__)

# Check if we are on local development machine (default is prod)
DEVELOPMENT = os.environ.get('DEVELOPMENT','FALSE')

# Connect to memcache with config from environment variables.
if DEVELOPMENT == 'TRUE':
	# Simple non-binary connection in case of development machine
	mc = pylibmc.Client(
	    servers=[os.environ.get('MEMCACHE_SERVERS','127.0.0.1')]
	)
else:
	mc = pylibmc.Client(
	    servers=[os.environ.get('MEMCACHE_SERVERS','127.0.0.1')],
	    username=os.environ.get('MEMCACHE_USERNAME',''),
	    password=os.environ.get('MEMCACHE_PASSWORD',''),
	    binary=True
	)

@app.route('/')
def index():
	return render_template('index.html')
	
@app.route('/getEphemerides', methods=['POST'])
def getEphemerides():
	lat = float(request.form['lat'])
	return json.dumps(sunazymuth.GetEphemerides(lat))

@app.route('/findMatch', methods=['POST'])
def findMatch():
	global mc
	# As request is unicode, we must transform it to a string to use as memcache key
	lat = request.form['lat'].encode('ascii','ignore')
	az = float(request.form['az'])
	# Get the fullyear calc from the cache
	if lat in mc:
		fullyear = mc.get(lat)
	else:
		fullyear = sunazymuth.GetEphemerides(float(lat))
		mc.set(lat, fullyear)
	return json.dumps(sunazymuth.GetMatchingDay(fullyear,az))

if __name__ == '__main__':
	#Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	debug = os.environ.get('DEBUG', True)
	app.run(host='0.0.0.0', port=port, debug=debug)
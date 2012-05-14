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

###
# Boiler-plate stuff from github/flask_heroku
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
	"""Send your static text file. robots.txt etc."""
	file_dot_text = file_name + '.txt'
	return app.send_static_file(file_dot_text)

@app.after_request
def add_header(response):
	"""
	Add headers to both force latest IE rendering engine or Chrome Frame,
	and also to cache the rendered page for 10 minutes.
	"""
	response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
	response.headers['Cache-Control'] = 'public, max-age=600'
	return response

@app.errorhandler(404)
def page_not_found(error):
	"""Custom 404 page."""
	return render_template('404.html'), 404


if __name__ == '__main__':
	#Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	debug = os.environ.get('DEBUG', True)
	app.run(host='0.0.0.0', port=port, debug=debug)
import sys
import os
import json
import redis
from urllib.parse import urlparse, urlunparse

import sunazymuth

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
app = Flask(__name__)


###
# APP ENVIRONMENT SETUP
###

# Check if we are on local development machine (default is prod)
DEVELOPMENT = os.environ.get('DEVELOPMENT', 'FALSE')

# Connect to Redis
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
r = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)

# Redirect herokuapp to custom domain
@app.before_request
def redirect_domain():
	urlparts = urlparse(request.url)
	if urlparts.netloc == 'sunsetter.herokuapp.com':
		urlparts_list = list(urlparts)
		urlparts_list[1] = 'www.sunset.io'
		return redirect(urlunparse(urlparts_list), code=301)


###
# APP WEB REQUEST HANDLERS
###

# Route for INDEX
@app.route('/')
def index():
	return render_template(
		'index.html',
		ANALYTICS=os.environ.get('ANALYTICS', 'UA-XXXXXX-1'),
		MAPS_API=os.environ.get('MAPS_API', '123456789')
	)


# Output a list of sunset and sunrise azymuth for the whole year
# NOT USED NOW
@app.route('/getEphemerides', methods=['POST'])
def getEphemerides():
	lat = float(request.form['lat'])
	return json.dumps(sunazymuth.GetEphemerides(lat))


# Find 2 days matching the given azymuth
# Returns in JSON:
#	- suntype = either "sunrise" or "sunset"
#	- matches = array of 2 matching days, nothing if azymuth is out of bounds
@app.route('/findMatch', methods=['POST'])
def findMatch():
	global r
	lat = request.form['lat']
	latkey = 'sunsetio:'+ lat
	az = float(request.form['az'])
	# Get the fullyear calc from the cache
	try:
		fullyear = r.get(latkey)
		if not fullyear:
			fullyear = sunazymuth.GetEphemerides(float(lat))
			r.set(latkey, json.dumps(fullyear))
		else:
			fullyear = json.loads(fullyear)
	except redis.RedisError as e:
		# If cache error, log the exception and compute the result anyway
		app.log_exception(e)
		fullyear = sunazymuth.GetEphemerides(float(lat))
	return json.dumps(sunazymuth.GetMatchingDay(fullyear, az))


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


###
# SERVER START
###

if __name__ == '__main__':
	#Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	debug = os.environ.get('DEBUG', False)
	app.run(host='0.0.0.0', port=port, debug=debug)

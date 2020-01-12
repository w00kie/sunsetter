import sys
import os
import json
from envparse import env
from urllib.parse import urlparse, urlunparse

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from flask_cdn import CDN

import sunazymuth

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect


###
# APP ENVIRONMENT SETUP
###

# Serve static files from web root
app = Flask(__name__, static_url_path='')

# Set static files location to CDN domain.
# Activates only when STATIC_DOMAIN env variable is set (only in Production)
app.config['CDN_DOMAIN'] = env('STATIC_DOMAIN', None)
CDN(app)

# Check if we are on local development machine (default is prod)
FLASK_ENV = env('FLASK_ENV', default='production')

sha = env('GIT_COMMIT_SHA1', default='')

SENTRY_DSN = env('SENTRY_DSN', default='')
sentry_sdk.init(
	dsn=SENTRY_DSN,
	environment=FLASK_ENV,
	release=sha,
	integrations=[FlaskIntegration()]
)


###
# APP WEB REQUEST HANDLERS
###

# Route for INDEX
@app.route('/')
def index():
	return render_template(
		'index.html',
		ANALYTICS=env('ANALYTICS', default='UA-XXXXXX-1'),
		MAPS_API=env('MAPS_API', default='123456789')
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
	lat = request.form['lat']
	az = float(request.form['az'])

	fullyear = sunazymuth.GetEphemerides(float(lat))

	return json.dumps(sunazymuth.GetMatchingDay(fullyear, az))


###
# Boiler-plate stuff from github/flask_heroku
###
'''
@app.route('/<file_name>.txt')
def send_text_file(file_name):
	"""Send your static text file. robots.txt etc."""
	file_dot_text = file_name + '.txt'
	return app.send_static_file(file_dot_text)
'''

@app.after_request
def add_header(response):
	# Add header to track Sentry release
	response.headers['X-Sentry-Release'] = sha
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

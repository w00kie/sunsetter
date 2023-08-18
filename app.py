from envparse import env

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from flask_cdn import CDN

from flask import Flask
from flask import request
from flask import render_template

import sunazymuth


###
# APP ENVIRONMENT SETUP
###

# Serve static files from web root
app = Flask(__name__, static_url_path="")

# Set static files location to CDN domain.
# Activates only when STATIC_DOMAIN env variable is set (only in Production)
app.config["CDN_DOMAIN"] = env("STATIC_DOMAIN", None)
app.config["CDN_HTTPS"] = True
CDN(app)

# Check if we are on local development machine (default is prod)
FLASK_ENV = env("FLASK_ENV", default="production")

sha = env("GIT_COMMIT_SHA1", default="")

SENTRY_DSN = env("SENTRY_DSN", default="")
sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment=FLASK_ENV,
    release=sha,
    integrations=[FlaskIntegration()],
)


###
# APP WEB REQUEST HANDLERS
###


# Route for INDEX
@app.route("/")
def index():
    return render_template(
        "index.html",
        ANALYTICS=env("ANALYTICS", default="UA-XXXXXX-1"),
        MAPS_API=env("MAPS_API", default="123456789"),
    )


# Output a list of sunset and sunrise azymuth for the whole year
# NOT USED NOW
@app.route("/getEphemerides", methods=["POST"])
def getEphemerides():
    lat = request.json["lat"]
    return sunazymuth.GetEphemerides(lat)


# Find 2 days matching the given azymuth
# Returns in JSON:
# 	- suntype = either "sunrise" or "sunset"
# 	- matches = array of 2 matching days, nothing if azymuth is out of bounds
@app.route("/findMatch", methods=["POST"])
def findMatch():
    data = request.json or request.form
    lat = data["lat"]
    az = float(data["az"])

    fullyear = sunazymuth.GetEphemerides(float(lat))

    return sunazymuth.GetMatchingDay(fullyear, az)


@app.after_request
def add_header(response):
    """
    Add headers to:
    - Track Sentry release
    - Force latest IE rendering engine or Chrome Frame,
    - Cache the rendered page for 10 minutes.
    """
    response.headers["X-Sentry-Release"] = sha
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=600"
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template("404.html", ERROR=error), 404

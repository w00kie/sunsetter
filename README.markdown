What is this?
=============
[Sunsetter](http://sunsetter.herokuapp.com) is a simple python web app running on Heroku that can calculate, given a point of view and a point of interest (selected on a google map) on which day of the year the sun will rise or set in this direction. More info on my [blog](http://w00kie.com/category/sunsetter-app/).

It is based on the brilliant [pysolar](http://pysolar.org/) library for the hardcore astronomical calculations. It also uses [spin.js](http://fgnass.github.com/spin.js/) for a cool Ajax spinner without any GIF.

**Note:** the app is configured to predict when the sun's _lower limb_ touches the horizon, not the _civil sunset_ when the sun completely disappears behind the horizon, as this makes for a better picture. This setting can be modified app-wide in `sunazymuth.py`.

How to run it on my machine?
============================
If you want to download it and run it on your own machine you must first install `venv` in the same folder and activate it:

    virtualenv venv --distribute
    source venv/bin/activate

This should change your prompt to include a `(venv)` prefix. Then install the pre-requirements with this command:

    pip install -r requirements.txt

Finally you need to add one environment variable to plug to local memcached without auth. Add the following to a `.env` file in the root folder:

    DEVELOPMENT=TRUE

You can then run locally with `foreman start -f Procfile.dev` which will start the python app as well as memcached and a coffee compiler to compile any changes to the javascript on the fly. Connect to the app in your browser on http://localhost:5000
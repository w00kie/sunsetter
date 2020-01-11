[![Actions Status](https://github.com/w00kie/sunsetter/workflows/Run%20linter%20and%20tests/badge.svg)](https://github.com/w00kie/sunsetter/actions)
[![Coverage Status](https://coveralls.io/repos/github/w00kie/sunsetter/badge.svg?branch=master)](https://coveralls.io/github/w00kie/sunsetter?branch=master)

What is this?
=============
[Sunsetter](http://www.sunset.io) is a simple python web app running on Heroku that can calculate, given a point of view and a point of interest (selected on a google map) on which day of the year the sun will rise or set in this direction. More info on my [blog](http://w00kie.com/category/sunsetter-app/).

It is based on the brilliant [pysolar](http://pysolar.org/) library for the hardcore astronomical calculations. It also uses [spin.js](http://fgnass.github.com/spin.js/) for a cool Ajax spinner without any GIF.

It's currently setup to self deploy and run on Google Cloud Run with Github Actions CI/CD.

**Note:** the app is configured to predict when the sun's _lower limb_ touches the horizon, not the _civil sunset_ when the sun completely disappears behind the horizon, as this makes for a better picture. This setting can be modified app-wide in `sunazymuth.py`.

How to run it on my machine?
============================
If you want to download it and run it on your own machine you can just run `docker-compose up` to run it on http://localhost:8000 with a redis instance. You'll need a Google Maps API key enabled for localhost though.

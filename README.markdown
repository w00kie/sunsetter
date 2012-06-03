What is this?
=============
[Sunsetter](http://sunsetter.herokuapp.com) is a simple python web app running on Heroku that can calculate, given a point of view and a point of interest (selected on a google map) on which day of the year the sun will rise or set in this direction. More info in my [blog post](http://w00kie.com/2012/05/17/pet-project-sunsetter/).

It is based on the brilliant [pysolar](http://pysolar.org/) library for the hardcore astronomical calculations. It also uses [spin.js](http://fgnass.github.com/spin.js/) for a cool Ajax spinner without any GIF.

How to run it on my machine?
============================
If you want to download it and run it on your own machine you must add one environment variable to plug to local memcached without auth. Add the following to a `.env` file in the root folder:

    DEVELOPMENT=TRUE

You can then run locally with `foreman start -f Procfile.dev` which will start the python app as well as memcached and a coffee compiler to compile any changes to the javascript on the fly.
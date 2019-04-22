#!/usr/bin/python

import math
import datetime
import time
from pysolar import solar

# Zenith angle of different phases of sunset
FULL_SUN = 89.75			# Lower limb touches horizon
HALF_SUN = 90				# Center of sun on horizon
CIVIL_SUNRISE = 90.833		# Top of sun appears over horizon (corrected for refraction)

# Setting used for application
SUNRISE_TYPE = FULL_SUN


# Closest matching value from a collection
def closest(target, collection):
	return min((abs(target - i), i) for i in collection)[1]


def GetSunriseAzymuth(lat, day):
	decl = math.radians(solar.get_declination(day))
	lat_rad = math.radians(lat)
	zenith_rad = math.radians(SUNRISE_TYPE)

	first_term = math.sin(lat_rad) * math.cos(zenith_rad) - math.sin(decl)
	second_term = math.cos(lat_rad) * math.sin(zenith_rad)
	return math.degrees(math.acos(-first_term / second_term))


def GetSunriseHourAngle(lat, day):
	decl = math.radians(solar.get_declination(day))
	lat_rad = math.radians(lat)
	zenith_rad = math.radians(SUNRISE_TYPE)

	first_term = math.cos(zenith_rad) / (math.cos(lat_rad) * math.cos(decl))
	second_term = math.tan(lat_rad) * math.tan(decl)
	return math.degrees(math.acos(first_term - second_term))


# Return timestamp for UTC time of Sunrise
def GetSunriseTime(lat, longitude, day):
	# get minutes from UTC midnight
	minutes = 720 + 4 * (-longitude - GetSunriseHourAngle(lat, day)) - solar.equation_of_time(day)
	# calculate the UTC time of sunrise
	sunrise = GetUTCMidnight(day) + datetime.timedelta(minutes=minutes)
	return GetTimestamp(sunrise)


# Return timestamp for UTC time of Sunset
def GetSunsetTime(lat, longitude, day):
	# get minutes from UTC midnight
	minutes = 720 + 4 * (-longitude + GetSunriseHourAngle(lat, day)) - solar.equation_of_time(day)
	# calculate the UTC time of sunset
	sunset = GetUTCMidnight(day) + datetime.timedelta(minutes=minutes)
	return GetTimestamp(sunset)


# Get sunset and sunrise azymuth for the whole year
def GetEphemerides(lat):
	fullyear = []
	for d in range(1, 366):
		sunriseaz = GetSunriseAzymuth(lat, d)
		sunsetaz = 360 - sunriseaz
		fullyear.append([sunriseaz, sunsetaz])
	return fullyear


# Find 2 matches to the given azymuth in a full year ephemerides list
def GetMatchingDay(fullyear, azimuth):
	# Keep just the sunset or sunrise depending on the given azymuth
	if (azimuth < 180):
		suntype = "Sunrise"
		fullyear = [sunrise for sunrise, sunset in fullyear]
	else:
		suntype = "Sunset"
		fullyear = [sunset for sunrise, sunset in fullyear]

	# If azymuth is out of bound, just return the suntype, no matching
	if (azimuth < min(fullyear) or azimuth > max(fullyear)):
		return {'suntype': suntype}

	# Cheating - we know roughly the solstice day, so we can work on half the problem
	summersolstice = 172
	wintersolstice = 356 - 365
	fallclosest = closest(azimuth, fullyear[summersolstice:wintersolstice])
	springclosest = closest(azimuth, fullyear[wintersolstice:] + fullyear[:summersolstice])

	# Format the day of year to a readable date
	matches = [GetDateFromDay(fullyear.index(springclosest)), GetDateFromDay(fullyear.index(fallclosest))]
	return ({'suntype': suntype, 'matches': matches})


# Format the day of year to something like "January 23"
def GetDateFromDay(day):
	today = datetime.date.today()
	thisyear = datetime.date(today.year, 1, 1)
	delta = datetime.timedelta(days=day - 1)
	d = thisyear + delta
	return d.strftime("%B %d")


# Returns UTC midnight datetime object from day of year
def GetUTCMidnight(day):
	timestr = "%s %s" % (datetime.datetime.now().year, day)
	return datetime.datetime.strptime(timestr, "%Y %j")


# Return POSIX timestamp from datetime object
def GetTimestamp(dt):
	return time.mktime(dt.timetuple())

#####
# DEBUG STUFF
#####
# print GetMatchingDay(35.8,99)

# d = datetime.datetime.utcnow()
# print GetSunriseAzymuth(-66, 0)
# print 360 - GetSunriseAzymuth(66, d)
# print GetSunriseTime(35.72, 139.7, d)
# print GetSunsetTime(35.72, 139.7, d)

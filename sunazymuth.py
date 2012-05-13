#!/usr/bin/python

import math
import datetime
from pysolar import solar

def closest(target, collection) :
    return min((abs(target - i), i) for i in collection)[1]

def GetSunriseAzymuth(lat, day):
	# day = solar.GetDayOfYear(utc_datetime)
	decl = math.radians(solar.GetDeclination(day))
	lat_rad = math.radians(lat)
	zenith_rad = math.radians(90.833)
	
	first_term = math.sin(lat_rad)*math.cos(zenith_rad)-math.sin(decl)
	second_term = math.cos(lat_rad)*math.sin(zenith_rad)
	return math.degrees(math.acos(-first_term/second_term))

def GetSunriseHourAngle(lat, day):
	# day = solar.GetDayOfYear(utc_datetime)
	decl = math.radians(solar.GetDeclination(day))
	lat_rad = math.radians(lat)
	zenith_rad = math.radians(90.833)
	
	first_term = math.cos(zenith_rad)/(math.cos(lat_rad)*math.cos(decl))
	second_term = math.tan(lat_rad)*math.tan(decl)
	return math.degrees(math.acos(first_term - second_term))

def GetSunriseTime(lat, longitude, day):
	# day = solar.GetDayOfYear(utc_datetime)
	minutes = 720 + 4*(-longitude - GetSunriseHourAngle(lat, utc_datetime)) - solar.EquationOfTime(day)
	return "%i:%i" % (minutes/60, minutes%60)

def GetSunsetTime(lat, longitude, day):
	# day = solar.GetDayOfYear(utc_datetime)
	minutes = 720 + 4*(-longitude + GetSunriseHourAngle(lat, utc_datetime)) - solar.EquationOfTime(day)
	return "%i:%i" % (minutes/60, minutes%60)
	
def GetEphemerides(lat):
	fullyear = []
	for d in range(1,365):
		sunriseaz = GetSunriseAzymuth(lat, d)
		sunsetaz = 360 - sunriseaz
		fullyear.append([sunriseaz, sunsetaz])
	return fullyear

def GetMatchingDay(fullyear, azimuth):
	if (azimuth < 180):
		suntype = "Sunrise"
		fullyear = [sunrise for sunrise,sunset in fullyear]
	else:
		suntype = "Sunset"
		fullyear = [sunset for sunrise,sunset in fullyear]
	
	if (azimuth < min(fullyear) or azimuth > max(fullyear)):
		return {'suntype':suntype}
	
	# Cheating - we know roughly the solstice day, so we can work on half the problem
	summersolstice = 172
	wintersolstice = 356-365
	fallclosest = closest(azimuth, fullyear[summersolstice:wintersolstice])
	springclosest = closest(azimuth, fullyear[wintersolstice:] + fullyear[:summersolstice])
	
	matches = [GetDateFromDay(fullyear.index(springclosest)), GetDateFromDay(fullyear.index(fallclosest))]
	return ({'suntype':suntype, 'matches':matches})

def GetDateFromDay (day):
	today = datetime.date.today()
	thisyear = datetime.date(today.year, 1, 1)
	delta = datetime.timedelta(days=day-1)
	d = thisyear + delta
	return d.strftime("%B %d")

# print GetMatchingDay(35.8,99)

# d = datetime.datetime.utcnow()
# print GetSunriseAzymuth(-66, 0)
# print 360 - GetSunriseAzymuth(66, d)
# print GetSunriseTime(35.72, 139.7, d)
# print GetSunsetTime(35.72, 139.7, d)
"""The original, field-tested Sunsetter solar alignment calculation."""

import datetime
import math

from pysolar import solar

FULL_SUN = 89.75  # Lower limb touches horizon.
SUNRISE_TYPE = FULL_SUN


def closest(target, collection):
    return min((abs(target - value), value) for value in collection)[1]


def GetSunriseAzymuth(lat, day):
    decl = math.radians(solar.get_declination(day))
    lat_rad = math.radians(lat)
    zenith_rad = math.radians(SUNRISE_TYPE)

    first_term = math.sin(lat_rad) * math.cos(zenith_rad) - math.sin(decl)
    second_term = math.cos(lat_rad) * math.sin(zenith_rad)
    return math.degrees(math.acos(-first_term / second_term))


def GetEphemerides(lat):
    fullyear = []
    for day in range(1, 366):
        sunrise_azimuth = GetSunriseAzymuth(lat, day)
        fullyear.append([sunrise_azimuth, 360 - sunrise_azimuth])
    return fullyear


def GetDateFromDay(day, year=None):
    this_year = datetime.date(year or datetime.date.today().year, 1, 1)
    return (this_year + datetime.timedelta(days=day - 1)).strftime("%B %d")


def GetMatchingDay(fullyear, azimuth, year=None):
    if azimuth < 180:
        sun_type = "Sunrise"
        fullyear = [sunrise for sunrise, _ in fullyear]
    else:
        sun_type = "Sunset"
        fullyear = [sunset for _, sunset in fullyear]

    if azimuth < min(fullyear) or azimuth > max(fullyear):
        return {"suntype": sun_type}

    summer_solstice = 172
    winter_solstice = 356 - 365
    fall_closest = closest(azimuth, fullyear[summer_solstice:winter_solstice])
    spring_closest = closest(
        azimuth, fullyear[winter_solstice:] + fullyear[:summer_solstice]
    )
    matches = [
        GetDateFromDay(fullyear.index(spring_closest), year),
        GetDateFromDay(fullyear.index(fall_closest), year),
    ]
    return {"suntype": sun_type, "matches": matches}


def ephemerides(latitude):
    return GetEphemerides(latitude)


def matching_days(latitude, azimuth, year=None):
    if not 0 <= azimuth < 360:
        raise ValueError("Azimuth must be between 0 and 360 degrees")

    year = year or datetime.date.today().year
    result = GetMatchingDay(GetEphemerides(latitude), azimuth, year)
    labels = result.get("matches", [])
    return {
        "suntype": result["suntype"],
        "matches": [
            datetime.datetime.strptime(f"{label} {year}", "%B %d %Y").date().isoformat()
            for label in labels
        ],
        "labels": [label.replace(" 0", " ") for label in labels],
    }

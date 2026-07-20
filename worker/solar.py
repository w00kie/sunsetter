"""Solar alignment calculations used by the Worker and local tests."""

from datetime import date, timedelta
from math import acos, cos, degrees, pi, radians, sin

HORIZON_ZENITH = 89.75  # Lower limb touches the horizon.


def solar_declination(day: int) -> float:
    """Approximate solar declination in degrees for a 1-based day of year."""
    return 23.45 * sin((2 * pi / 365) * (284 + day))


def sunrise_azimuth(latitude: float, day: int) -> float:
    declination = radians(solar_declination(day))
    latitude_radians = radians(latitude)
    zenith = radians(HORIZON_ZENITH)
    numerator = sin(latitude_radians) * cos(zenith) - sin(declination)
    denominator = cos(latitude_radians) * sin(zenith)
    value = max(-1.0, min(1.0, -numerator / denominator))
    return degrees(acos(value))


def ephemerides(latitude: float) -> list[tuple[float, float]]:
    if not -66 <= latitude <= 66:
        raise ValueError("Latitude must be between -66 and 66 degrees")
    return [(azimuth := sunrise_azimuth(latitude, day), 360 - azimuth) for day in range(1, 366)]


def _closest_index(values: list[float], target: float, indexes: range) -> int:
    return min(indexes, key=lambda index: abs(values[index] - target))


def matching_days(latitude: float, azimuth: float, year: int | None = None) -> dict:
    if not 0 <= azimuth < 360:
        raise ValueError("Azimuth must be between 0 and 360 degrees")

    year = year or date.today().year
    annual = ephemerides(latitude)
    sun_type = "Sunrise" if azimuth < 180 else "Sunset"
    values = [pair[0 if sun_type == "Sunrise" else 1] for pair in annual]

    if azimuth < min(values) or azimuth > max(values):
        return {"suntype": sun_type, "matches": []}

    # Each alignment occurs once on either side of the summer solstice.
    first = _closest_index(values, azimuth, range(0, 172))
    second = _closest_index(values, azimuth, range(172, 365))
    start = date(year, 1, 1)
    dates = [start + timedelta(days=index) for index in sorted((first, second))]

    return {
        "suntype": sun_type,
        "matches": [value.isoformat() for value in dates],
        "labels": [value.strftime("%B %-d") for value in dates],
    }


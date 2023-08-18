from app import app

from .helpers import format_day


def test_homepage_view():
    """Homepage returns HTTP 200"""
    response = app.test_client().get("/")
    assert response.status_code == 200


def test_ephemerides_view():
    """Ephemerides endpoint returns HTTP 200"""
    response = app.test_client().post("/getEphemerides", json={"lat": 42})
    assert response.status_code == 200


def test_robotstxt():
    """Robots.txt must contain User-agent: *"""
    response = app.test_client().get("/robots.txt")
    assert b"User-agent: *" in response.data


def test_404():
    """404 page works"""
    response = app.test_client().get("/missing")
    assert response.status_code == 404


def test_champs_elysees():
    """Champs Elysees sunset alignment matches"""
    response = app.test_client().post(
        "/findMatch", json={"lat": 48.9, "az": 295.6}, follow_redirects=True
    )
    # Must match ['May 06', 'August 04']
    assert response.json == {
        "suntype": "Sunset",
        "matches": [format_day(126), format_day(216)],
    }


def test_manhattanhenge():
    """Manhattanhenge alignment matches"""
    response = app.test_client().post("/findMatch", json={"lat": 40.8, "az": 299.18})
    # Must match ['May 30', 'July 12']
    assert response.json == {
        "suntype": "Sunset",
        "matches": [format_day(150), format_day(193)],
    }


def test_sunrise():
    """Sunrises must also match"""
    response = app.test_client().post("/findMatch", json={"lat": 1.4, "az": 112.82})
    # Must match ['January 02', 'December 06']
    assert response.json == {
        "suntype": "Sunrise",
        "matches": [format_day(2), format_day(340)],
    }


def test_no_match():
    """Looking directly south does not find a match"""
    response = app.test_client().post(
        "/findMatch", json={"lat": 5, "az": 190}, follow_redirects=True
    )
    assert response.json == {"suntype": "Sunset"}


def test_ephemerides_data():
    """Ephemerides must return sunsets for a year"""
    response = app.test_client().post("/getEphemerides", json={"lat": 42})
    assert len(response.json) == 365

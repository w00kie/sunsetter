import unittest

from flask import json
from flask_testing import TestCase

from app import app


class TestBase(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        pass
    
    def tearDown(self):
        pass


class TestViews(TestBase):
    def test_homepage_view(self):
        """Homepage returns HTTP 200"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_ephemerides_view(self):
        """Ephemerides endpoint returns HTTP 200"""
        response = self.client.post('/getEphemerides', data=dict(lat=42))
        self.assertEqual(response.status_code, 200)
    
    def test_robotstxt(self):
        """Robots.txt must contain User-agent: *"""
        response = self.client.get('/robots.txt')
        self.assertIn(b'User-agent: *', response.data)
    
    def test_redirect_from_heroku(self):
        """Calls to heroku must be redirected to new domain"""
        response = self.client.get('/', base_url='https://sunsetter.herokuapp.com')
        self.assertEqual(response.status_code, 301)

    def test_404(self):
        """404 page works"""
        response = self.client.get('/missing')
        self.assertEqual(response.status_code, 404)


class TestData(TestBase):
    def test_champs_elysees(self):
        """Champs Elysees sunset alignment matches"""
        response = self.client.post('/findMatch', data=dict(
                lat=48.9,
                az=295.6
            ),
            follow_redirects=True
        )
        self.assertEquals(
            json.loads(response.data), 
            dict(
                suntype='Sunset',
                matches=['May 06', 'August 04']
            )
        )

    def test_manhattanhenge(self):
        """Manhattanhenge alignment matches"""
        response = self.client.post('/findMatch', data=dict(
                lat=40.8,
                az=299.18
            )
        )
        self.assertEquals(
            json.loads(response.data), 
            dict(
                suntype='Sunset',
                matches=['May 30', 'July 12']
            )
        )

    def test_sunrise(self):
        """Sunrises must also match"""
        response = self.client.post('/findMatch', data=dict(
                lat=1.4,
                az=112.82
            )
        )
        self.assertEquals(
            json.loads(response.data), 
            dict(
                suntype='Sunrise',
                matches=['January 02', 'December 06']
            )
        )

    def test_no_match(self):
        """Looking directly south does not find a match"""
        response = self.client.post('/findMatch', data=dict(
                lat=5,
                az=190
            ),
            follow_redirects=True
        )
        self.assertEquals(
            json.loads(response.data), 
            dict(
                suntype='Sunset'
            )
        )
    
    def test_ephemerides_data(self):
        """Ephemerides must return sunsets for a year"""
        response = self.client.post('/getEphemerides', data=dict(lat=42))
        self.assertEqual(len(json.loads(response.data)), 365)

if __name__ == '__main__':
    unittest.main()
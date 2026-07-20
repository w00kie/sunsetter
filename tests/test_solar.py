import unittest

from worker.solar import ephemerides, matching_days


class SolarTests(unittest.TestCase):
    def test_manhattanhenge(self):
        result = matching_days(40.8, 299.18, 2026)
        self.assertEqual(result["suntype"], "Sunset")
        self.assertEqual(result["matches"], ["2026-05-31", "2026-07-13"])

    def test_sunrise(self):
        result = matching_days(1.4, 112.82, 2026)
        self.assertEqual(result["suntype"], "Sunrise")
        self.assertEqual(result["matches"], ["2026-01-03", "2026-12-07"])

    def test_impossible_direction(self):
        self.assertEqual(matching_days(5, 190, 2026)["matches"], [])

    def test_full_year(self):
        self.assertEqual(len(ephemerides(42)), 365)

    def test_rejects_polar_latitudes(self):
        with self.assertRaisesRegex(ValueError, "Latitude"):
            ephemerides(80)


if __name__ == "__main__":
    unittest.main()


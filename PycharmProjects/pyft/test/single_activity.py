import unittest
from datetime import timedelta

import gpxpy
from pyft.single_activity import Activity

TEST_DATA = '/home/alan/bin/PycharmProjects/pyft/test/test_data/activity_4037789130.gpx'


class ActivityAnalysisTestCase(unittest.TestCase):

    def setUp(self):
        with open(TEST_DATA) as f:
            self.gpx = gpxpy.parse(f)
            self.activity = Activity.from_gpx(self.gpx)

    def test_time(self):
        self.assertEqual(self.activity.date_time, self.gpx.time)
        self.assertEqual(self.activity.total_time, timedelta(hours=1, minutes=56, seconds=59))

    def test_distance(self):
        self.assertAlmostEqual(self.activity.distance_2d, self.gpx.length_2d())


if __name__ == '__main__':
    unittest.main()

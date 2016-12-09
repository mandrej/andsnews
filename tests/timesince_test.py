import unittest
from datetime import datetime, timedelta

# from config import timesince_jinja


# class TimesinceTest(unittest.TestCase):
#     def setUp(self):
#         self.now = datetime.now()
#
#     def test_timesince(self):
#         s = timesince_jinja(self.now - timedelta(minutes=2))
#         self.assertEqual(s, '2 minutes')
#
#         s = timesince_jinja(self.now - timedelta(hours=2))
#         self.assertEqual(s, '2 hours')
#
#         s = timesince_jinja(self.now - timedelta(days=2))
#         self.assertEqual(s, '2 days')
#
#         s = timesince_jinja(self.now - timedelta(weeks=2))
#         self.assertEqual(s, '2 weeks')
#
#         s = timesince_jinja(self.now - timedelta(weeks=2))
#         self.assertEqual(s, '2 weeks')
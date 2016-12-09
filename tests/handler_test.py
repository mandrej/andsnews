import unittest

import webapp2

import main


# class HandlerTest(unittest.TestCase):
#     def test_Sign(self):
#         req = webapp2.Request.blank('/sign')
#         res = req.get_response(main.app)
#         location = res.headers.get('Location')
#         print location
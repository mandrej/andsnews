__author__ = 'milan'

import unittest
import urllib2
from timer import Timer
from google.appengine.api import urlfetch
from contextlib import closing


class FeedTest(unittest.TestCase):
    def setUp(self):
        self.url = 'http://feeds.nationalgeographic.com/ng/News/News_Main'

    def test_rpc_urlfetch(self):
        with Timer() as target:
            rpc = urlfetch.create_rpc(deadline=20)
            urlfetch.make_fetch_call(rpc, self.url)
            result = rpc.get_result()
        print 'rpc_urlfetch in %.2f ms' % target.elapsed

    def test_urlfetch(self):
        with Timer() as target:
            result = urlfetch.fetch(self.url)
        print 'urlfetch in %.2f ms' % target.elapsed

    def test_urllib2(self):
        with Timer() as target:
            with closing(urllib2.urlopen(self.url)) as sf:
                sf.read()
        print 'urllib2 in %.2f ms' % target.elapsed
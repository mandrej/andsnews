# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

import unittest
from lib.babel.messages import tests as messages
from lib.babel.tests import support, dates, core, numbers, util, plural, localedata

def suite():
    suite = unittest.TestSuite()
    suite.addTest(core.suite())
    suite.addTest(dates.suite())
    suite.addTest(localedata.suite())
    suite.addTest(messages.suite())
    suite.addTest(numbers.suite())
    suite.addTest(plural.suite())
    suite.addTest(support.suite())
    suite.addTest(util.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

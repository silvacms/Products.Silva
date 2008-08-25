# -*- coding: utf-8 -*-
# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from pkg_resources import resource_listdir

from zope.testing import doctest

from Products.Silva.tests.layer import SilvaZCMLLayer

def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'Products.Silva.tests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(dottedname,
                                    optionflags=doctest.ELLIPSIS + \
                                        doctest.NORMALIZE_WHITESPACE)
        test.layer = SilvaZCMLLayer
        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(suiteFromPackage('grok'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

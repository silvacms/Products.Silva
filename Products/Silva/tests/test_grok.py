# -*- coding: utf-8 -*-
# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import doctest
import unittest

from Products.Silva.testing import FunctionalLayer, suite_from_package
from infrae.testbrowser.browser import Browser
from zope.interface.verify import verifyObject


globs = {
    'Browser': lambda: Browser(FunctionalLayer._test_wsgi_application),
    'verifyObject': verifyObject,
    'get_root': FunctionalLayer.get_application,
    'grok': FunctionalLayer.grok,}


def create_test(build_test_suite, name):
    test =  build_test_suite(
        name,
        globs=globs,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)
    test.layer = FunctionalLayer
    return test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(suite_from_package('Products.Silva.tests.grok', create_test))
    return suite

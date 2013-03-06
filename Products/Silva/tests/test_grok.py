# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import doctest
import unittest

from Products.Silva.testing import FunctionalLayer, suite_from_package
from zope.interface.verify import verifyObject


globs = {
    'verifyObject': verifyObject,
    'get_browser': FunctionalLayer.get_browser,
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

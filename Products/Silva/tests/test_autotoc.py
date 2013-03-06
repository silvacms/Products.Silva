# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import IAutoTOC
from zope.interface.verify import verifyObject

from Products.Silva.ftesting import public_settings
from Products.Silva.testing import FunctionalLayer


class AutoTOCTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addAutoTOC('toc', 'Table of content')

    def test_autotoc(self):
        """Test AutoTOC content type.
        """
        self.assertTrue(verifyObject(IAutoTOC, self.root.toc))

    def test_view(self):
        """Test the public view of an autotoc.
        """
        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(browser.open('/root/toc'), 200)
            self.assertEqual(browser.inspect.title, ['Table of content'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AutoTOCTestCase))
    return suite

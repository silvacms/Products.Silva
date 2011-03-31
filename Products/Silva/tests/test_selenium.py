# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer
from infrae.testbrowser.selenium import Browser

class SeleniumTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_boot(self):
        browser = Browser(self.layer.get_wsgi_application())
        browser.login('manager')
        browser.open('/root/edit')
        self.assertEqual(browser.location, '/root/edit')
        self.assertEqual(browser.url, 'http://localhost:8000/root/edit')
        browser.inspect.add('screens', xpath='//a[contains(@class, "open-screen")]', type='link')
        browser.inspect.screens['preview'].click()
        browser.close()

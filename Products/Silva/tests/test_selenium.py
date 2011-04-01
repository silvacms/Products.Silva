# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer

class SeleniumTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_boot(self):
        browser = self.layer.get_selenium_browser()
        browser.login('manager')
        browser.open('/root/edit')
        self.assertEqual(browser.location, '/root/edit')
        self.assertEqual(browser.url, 'http://localhost:8000/root/edit')
        browser.inspect.add('screens', xpath='//a[contains(@class, "open-screen")]', type='link')
        browser.inspect.add('controls', xpath='//a[contains(@class, "form-control")]', type='link')
        browser.inspect.screens['add'].click()
        browser.inspect.screens['silva folder'].click()
        form = browser.get_form('addform')
        control = form.get_control('addform.field.id')
        control.value = 'folder'
        control = form.get_control('addform.field.title')
        control.value = 'Folder'
        browser.inspect.controls['save'].click()

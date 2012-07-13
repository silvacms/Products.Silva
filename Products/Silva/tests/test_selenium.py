# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings


class SeleniumTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_add_folder(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager')
        browser.open('/root/edit')
        self.assertEqual(browser.location, '/root/edit')

        browser.inspect.content_tabs['add'].click()
        browser.inspect.content_subtabs['silva folder'].click()

        form = browser.get_form('addform')
        control = form.get_control('addform.field.id')
        control.value = 'folder'
        control = form.get_control('addform.field.title')
        control.value = 'Folder'

        browser.inspect.form_controls['save'].click()


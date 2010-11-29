# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings


class FeedsTestCase(unittest.TestCase):
    """Test properties tab of a Folder.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Test Folder')

    def test_feeds(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/folder/atom.xml'), 404)
        self.assertEqual(browser.open('/root/folder/rss.xml'), 404)

        self.assertEqual(browser.open('/root/folder/edit'), 200)

        self.assertTrue('properties' in browser.inspect.tabs)
        self.assertEqual(browser.inspect.tabs['properties'].click(), 200)
        self.assertEqual(browser.location, '/root/folder/edit/tab_metadata')

        self.assertTrue('settings' in browser.inspect.subtabs)
        self.assertEqual(browser.inspect.subtabs['settings'].click(), 200)
        self.assertEqual(browser.location, '/root/folder/edit/tab_settings')

        form = browser.get_form('settingsform')
        self.assertEqual(form.get_control('allow_feeds').checked, False)
        form.get_control('allow_feeds').checked = True
        self.assertEqual(
            form.get_control('tab_settings_save_feeds:method').click(),
            200)
        self.assertEqual(browser.inspect.feedback, ['Feed settings saved.'])

        self.assertEqual(browser.open('/root/folder/atom.xml'), 200)
        self.assertEqual(browser.content_type, 'text/xml;charset=UTF-8')
        self.assertEqual(browser.open('/root/folder/rss.xml'), 200)
        self.assertEqual(browser.content_type, 'text/xml;charset=UTF-8')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FeedsTestCase))
    return suite

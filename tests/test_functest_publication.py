# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings

class EditorPublicationTestCase(unittest.TestCase):
    layer = FunctionalLayer
    username = 'editor'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addLink(
            'link', 'Link', relative=False, url='http://infrae.com')

    def test_quick_publish(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login(self.username)

        self.assertEqual(browser.open('/root/link/edit'), 200)

        # By default content not publish, can edit it.
        form = browser.get_form('editform')
        self.assertTrue(len(form.controls))
        self.assertEqual(browser.get_link('view public version').click(), 200)

        # Link is not published, so can't view it.
        self.assertEqual(browser.url, '/root/link')
        self.assertTrue(
            'Sorry, this Silva Link is not viewable.' in browser.contents)
        self.assertEqual(self.root.link.get_viewable(), None)

        # Now publish the link.
        self.assertEqual(browser.open('/root/link/edit'), 200)
        form = browser.get_form('md.version')
        self.assertEqual(
            form.get_control('md.version.action.publish-now').click(),
            200)
        self.assertEqual(
            browser.inspect.feedback,
            ['Version approved.'])

         # Can edit the content anymore.
        form = browser.get_form('editform')
        self.assertFalse(len(form.controls))
        self.assertEqual(self.root.link.get_editable(), None)

        browser.options.follow_redirect = False
        self.assertEqual(browser.get_link('view public version').click(), 302)
        self.assertEqual(browser.headers['Location'], 'http://infrae.com')
        self.assertNotEqual(self.root.link.get_viewable(), None)
        browser.options.follow_redirect = True

        # Now create a new version
        self.assertEqual(browser.open('/root/link/edit'), 200)
        form = browser.get_form('md.version')
        self.assertEqual(
            form.get_control('md.version.action.new-version').click(),
            200)
        self.assertEqual(
            browser.inspect.feedback,
            ['New version created.'])

        # And content is now editable.
        form = browser.get_form('editform')
        self.assertTrue(len(form.controls))
        self.assertNotEqual(self.root.link.get_editable(), None)
        self.assertNotEqual(self.root.link.get_viewable(), None)


class ChiefEditorPublicationTestCase(EditorPublicationTestCase):
    username = 'chiefeditor'


class ManagerPublicationTestCase(EditorPublicationTestCase):
    username = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EditorPublicationTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorPublicationTestCase))
    suite.addTest(unittest.makeSuite(ManagerPublicationTestCase))
    return suite

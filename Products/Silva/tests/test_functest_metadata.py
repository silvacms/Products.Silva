# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings


class AuthorMetadataTestCase(unittest.TestCase):
    layer = FunctionalLayer
    username = 'author'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')

    def test_metadata(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.username, self.username)

        self.assertEqual(browser.open('/root/document/edit'), 200)

        self.assertTrue('properties' in browser.inspect.tabs)
        self.assertEqual(browser.inspect.tabs['properties'].click(), 200)
        self.assertEqual(browser.url, '/root/document/edit/tab_metadata')

        # Metadata main set.
        form = browser.get_form('form')
        form.get_control('silva-content.maintitle:record').value = \
            u'content €€€€ title'
        form.get_control('silva-content.shorttitle:record').value = \
            u'content €€€€ shorttitle'
        self.assertEqual(
            form.get_control('save_metadata:method').click(),
            200)
        self.assertEqual(
            browser.inspect.feedback,
            ['Metadata saved.'])

        form = browser.get_form('form')
        self.assertEqual(
            form.get_control('silva-content.maintitle:record').value,
            u'content €€€€ title')
        self.assertEqual(
            form.get_control('silva-content.shorttitle:record').value,
            u'content €€€€ shorttitle')

        # Metadata extra set.
        form = browser.get_form('form')
        form.get_control('silva-extra.subject:record').value = \
            u'content €€€€ subject'
        form.get_control('silva-extra.keywords:record').value = \
            u'keyword ¥¥¥¥ value'
        form.get_control('silva-extra.content_description:record').value = \
            u'description in $$$ and €€€€ and ££££ and ¥¥¥¥'
        form.get_control('silva-extra.comment:record').value = \
            u'comment value in ££££'
        form.get_control('silva-extra.contactname:record').value = \
            u'wim $$$$'
        form.get_control('silva-extra.contactemail:record').value = \
            u'wim@example.com'
        self.assertEqual(
            form.get_control('silva-extra.hide_from_tocs:record').options,
            ['do not hide', 'hide'])
        form.get_control('silva-extra.hide_from_tocs:record').value = 'hide'
        self.assertEqual(
            form.get_control('save_metadata:method').click(),
            200)
        self.assertEqual(
            browser.inspect.feedback,
            ['Metadata saved.'])


        form = browser.get_form('form')
        self.assertEqual(
            form.get_control('silva-extra.subject:record').value,
            u'content €€€€ subject')
        self.assertEqual(
            form.get_control('silva-extra.keywords:record').value,
            u'keyword ¥¥¥¥ value')
        self.assertEqual(
            form.get_control('silva-extra.content_description:record').value,
            u'description in $$$ and €€€€ and ££££ and ¥¥¥¥')
        self.assertEqual(
            form.get_control('silva-extra.comment:record').value,
            u'comment value in ££££')
        self.assertEqual(
            form.get_control('silva-extra.contactname:record').value,
            u'wim $$$$')
        self.assertEqual(
            form.get_control('silva-extra.contactemail:record').value,
            u'wim@example.com')
        self.assertEqual(
            form.get_control('silva-extra.hide_from_tocs:record').value,
            'hide')


class EditorMetadataTestCase(AuthorMetadataTestCase):
    username = 'editor'


class ChiefEditorMetadataTestCase(EditorMetadataTestCase):
    username = 'chiefeditor'


class ManagerMetadataTestCase(ChiefEditorMetadataTestCase):
    username = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorMetadataTestCase))
    suite.addTest(unittest.makeSuite(EditorMetadataTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorMetadataTestCase))
    suite.addTest(unittest.makeSuite(ManagerMetadataTestCase))
    return suite

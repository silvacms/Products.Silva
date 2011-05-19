# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from Products.Silva.testing import FunctionalLayer, smi_settings


class AuthorAddablesTestCase(unittest.TestCase):
    """An author doesn't have any setting tab nor addable one.
    """
    layer = FunctionalLayer
    username = 'author'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

    def test_addables(self):
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login(self.username)

        browser.open('/root/edit')
        self.assertFalse('settings' in browser.inspect.content_tabs)


class EditorAddablesTestCase(AuthorAddablesTestCase):
    """An editor have a setting tab but no addable.
    """
    username = 'editor'

    def test_addables(self):
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login(self.username)

        browser.open('/root/edit')
        self.assertTrue('settings' in browser.inspect.content_tabs)

        browser.inspect.content_tabs['settings'].click()
        self.assertFalse('addables' in browser.inspect.content_subtabs)


class ChiefEditorAddablesTestCase(EditorAddablesTestCase):
    """ChiefEditor (and Manager) have a setting tab and a addable one.
    """
    username = 'chiefeditor'

    def test_addables(self):
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login(self.username)

        browser.open('/root/edit')
        self.assertTrue('settings' in browser.inspect.content_tabs)

        browser.inspect.content_tabs['settings'].click()
        self.assertTrue('addables' in browser.inspect.content_subtabs)

        browser.inspect.content_subtabs['addables'].click()

        # Addables form: change addables
        form = browser.get_form('form')
        addables = form.get_control('form.field.addables')
        self.assertTrue('Silva File' in addables.options)
        self.assertTrue('Silva Image' in addables.options)
        self.assertTrue('Silva Folder' in addables.options)
        self.assertTrue('Silva Publication' in addables.options)

        addables.value = ['Silva Folder', 'Silva File', 'Silva Image']
        browser.inspect.form_controls['save'].click()

        self.assertListEqual(
            browser.inspect.feedback,
            ['Changes to addables content types saved.'])

        form = browser.get_form('form')
        self.assertItemsEqual(
            form.get_control('form.field.addables').value,
            ['Silva Folder', 'Silva File', 'Silva Image'])

        return
        # Go back on container view.
        self.assertEqual(browser.inspect.tabs['contents'].click(), 200)
        self.assertEqual(browser.url, '/root/edit/tab_edit')

        # Only Folder, File and Image are addable now.
        form = browser.get_form('md.container')
        self.assertEqual(
            form.get_control('md.container.field.content').options,
            ['none', 'Silva Folder', 'Silva File', 'Silva Image'])
        self.assertEqual(
            form.get_control('md.container.action.new').click(),
            200)

        # Go on generic add view, it is the same.
        self.assertEqual(browser.url, '/root/edit/+')
        self.assertEqual(
            browser.html.xpath('//dl[@class="new-content-listing"]//a/text()'),
            ['Silva Folder', 'Silva File', 'Silva Image'])
        self.assertEqual(
            browser.html.xpath('//dl[@class="new-content-listing"]//a/@href'),
            ['http://localhost/root/edit/+/Silva Folder',
             'http://localhost/root/edit/+/Silva File',
             'http://localhost/root/edit/+/Silva Image'])

        # Access something which is not addable makes a redirect to +
        self.assertEqual(browser.open('/root/edit/+/Silva Document'), 200)
        self.assertEqual(browser.url, '/root/edit/+')

        # Go on folder content, child of this root. Settings are acquired.
        self.assertEqual(browser.inspect.tabs['content'].click(), 200)
        self.assertEqual(browser.inspect.folder_listing['folder'].click(), 200)
        self.assertEqual(browser.url, '/root/folder/edit/tab_edit')

        # Visit addable tab on this folder.
        self.assertTrue('properties' in browser.inspect.tabs)
        self.assertEqual(browser.inspect.tabs['properties'].click(), 200)

        self.assertTrue('addables' in browser.inspect.subtabs)
        self.assertEqual(browser.inspect.subtabs['addables'].click(), 200)
        self.assertEqual(browser.url, '/root/folder/edit/tab_addables')

        form = browser.get_form('form')
        self.assertEqual(
            form.get_control('field_acquire_addables').checked,
            True)
        self.assertEqual(
            form.get_control('field_addables').value,
            ['Silva Folder', 'Silva File', 'Silva Image'])


class ManagerAddablesTestCase(ChiefEditorAddablesTestCase):
    username = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorAddablesTestCase))
    suite.addTest(unittest.makeSuite(EditorAddablesTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorAddablesTestCase))
    suite.addTest(unittest.makeSuite(ManagerAddablesTestCase))
    return suite

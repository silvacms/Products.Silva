# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import transaction
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
        transaction.commit()

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

        # Now check the add menu: only the three selected are there
        self.assertTrue('add' in browser.inspect.content_tabs)

        browser.inspect.content_tabs['add'].click()
        self.assertItemsEqual(
            browser.inspect.content_subtabs.keys(),
            ['Silva Folder', 'Silva File', 'Silva Image'])

        # Visit addable tab on this folder.
        self.assertTrue('content' in browser.inspect.content_tabs)
        browser.inspect.content_tabs['content'].click()

        # We have one folder, with an addable tab as well
        self.assertEqual(browser.inspect.folder_identifier, ['folder'])
        browser.inspect.folder_goto[0].click()

        self.assertTrue('settings' in browser.inspect.content_tabs)

        browser.inspect.content_tabs['settings'].click()
        self.assertTrue('addables' in browser.inspect.content_subtabs)

        browser.inspect.content_subtabs['addables'].click()

        # There is a form, where settings are acquired.
        form = browser.get_form('form')
        self.assertEqual(
            form.get_control('form.field.acquire').checked,
            True)
        self.assertItemsEqual(
            form.get_control('form.field.addables').value,
            ['Silva Folder', 'Silva File', 'Silva Image'])

        # And we can only add acquired values
        self.assertTrue('add' in browser.inspect.content_tabs)

        browser.inspect.content_tabs['add'].click()
        self.assertItemsEqual(
            browser.inspect.content_subtabs.keys(),
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

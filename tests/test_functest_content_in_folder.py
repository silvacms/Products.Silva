# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings
from Products.Silva.tests.helpers import test_filename
from silva.core.references.reference import get_content_id


class ContentTypeInFolderTestCase(unittest.TestCase):
    """Each role make each content type in a folder.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_document(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Folder',
            id='folder', title='First Folder', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Folder'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Document', id='documentation', title='Documentation')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'documentation'])
            browser.macros.delete('documentation')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.navigation['root'].click(), 200)
        browser.macros.delete('folder')

    def test_folder(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Folder',
            id='folder', title='First Folder', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Folder'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Folder',
                id='folder', title='Second Folder', default_item='Silva Document')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'folder'])
            browser.macros.delete('folder')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.navigation['root'].click(), 200)
        browser.macros.delete('folder')

    def test_publication(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Folder',
            id='folder', title='First Folder', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Folder'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Publication',
                id='publication', title='Second Publication', default_item='Silva Document')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'publication'])
            browser.macros.delete('publication')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.navigation['root'].click(), 200)
        browser.macros.delete('folder')

    def test_image(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Folder',
            id='folder', title='First Folder', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Folder'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            image = test_filename('torvald.jpg')
            browser.login(user, user)
            browser.macros.create(
                'Silva Image', id='image', title='Torvald', file=image)
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'image'])
            browser.macros.delete('image')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.navigation['root'].click(), 200)
        browser.macros.delete('folder')

    def test_file(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Folder',
            id='folder', title='First Folder', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Folder'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            image = test_filename('torvald.jpg')
            browser.login(user, user)
            browser.macros.create(
                'Silva File', id='file', title='Text File', file=image)
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'file'])
            browser.macros.delete('file')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.navigation['root'].click(), 200)
        browser.macros.delete('folder')

    def test_find(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Folder',
            id='folder', title='First Folder', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Folder'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Find', id='search', title='Search')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'search'])
            browser.macros.delete('search')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.navigation['root'].click(), 200)
        browser.macros.delete('folder')

    def test_ghost(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Folder',
            id='folder', title='First Folder', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Folder'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Ghost',
                id='ghost', haunted=get_content_id(self.root.index))
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'ghost'])
            browser.macros.delete('ghost')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.navigation['root'].click(), 200)
        browser.macros.delete('folder')

    def test_indexer(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Folder',
            id='folder', title='First Folder', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Folder'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Indexer', id='indexes', title='Indexes')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'indexes'])
            browser.macros.delete('indexes')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.navigation['root'].click(), 200)
        browser.macros.delete('folder')

    def test_link(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Folder',
            id='folder', title='First Folder', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Folder'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Link',
                id='infrae', title='Infrae', url='http://infrae.com')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'infrae'])
            browser.macros.delete('infrae')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.navigation['root'].click(), 200)
        browser.macros.delete('folder')

    def test_autotoc(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Folder',
            id='folder', title='First Folder', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Folder'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            browser.macros.create(
                'Silva AutoTOC', id='sitemap', title='Sitemap')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'sitemap'])
            browser.macros.delete('sitemap')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.navigation['root'].click(), 200)
        browser.macros.delete('folder')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentTypeInFolderTestCase))
    return suite

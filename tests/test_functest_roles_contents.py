# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings
from Products.Silva.tests.helpers import test_filename
from silva.core.references.reference import get_content_id


class ContentCreationTestCase(unittest.TestCase):
    """For each role make each content in a folder.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_document(self):
        browser = self.layer.get_browser(smi_settings)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            self.assertEqual(browser.open('/root/edit'), 200)
            browser.macros.create(
                'Silva Document', id='documentation', title='Documentation')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'documentation'])

            # The user should by the last author on the content and container.
            content = self.root
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.documentation
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['documentation'].click(), 200)
            self.assertEqual(
                browser.url, '/root/documentation/edit/tab_edit')
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'documentation'])
            browser.inspect.breadcrumbs['root'].click()
            browser.macros.delete('documentation')

    def test_folder(self):
        browser = self.layer.get_browser(smi_settings)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            self.assertEqual(browser.open('/root/edit'), 200)
            browser.macros.create(
                'Silva Folder',
                id='folder',
                title='Second Folder',
                default_item='Silva Document')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'folder'])

            # The user should by the last author on the content and container.
            content = self.root
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.folder
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['folder'].click(),
                200)
            self.assertEqual(
                browser.url, '/root/folder/edit/tab_edit')
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'Second Folder'])
            browser.inspect.breadcrumbs['root'].click()
            browser.macros.delete('folder')

    def test_publication(self):
        browser = self.layer.get_browser(smi_settings)

        for user in ['manager', 'chiefeditor', 'editor']:
            browser.login(user, user)
            self.assertEqual(browser.open('/root/edit'), 200)
            browser.macros.create(
                'Silva Publication',
                id='publication',
                title='Second Publication',
                default_item='Silva Document')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'publication'])

            # The user should by the last author on the content and container.
            content = self.root
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.publication
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['publication'].click(),
                200)
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'Second Publication'])
            browser.inspect.breadcrumbs['root'].click()
            browser.macros.delete('publication')

    def test_image(self):
        browser = self.layer.get_browser(smi_settings)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            image = test_filename('torvald.jpg')
            browser.login(user, user)
            self.assertEqual(browser.open('/root/edit'), 200)
            browser.macros.create(
                'Silva Image', id='image', title='Torvald', file=image)
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'image'])

            # The user should by the last author on the content and container.
            content = self.root
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.image
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['image'].click(),
                200)
            self.assertEqual(browser.url, '/root/image/edit/tab_edit')
            self.assertEqual(browser.inspect.breadcrumbs, ['root', 'Torvald'])
            browser.inspect.breadcrumbs['root'].click()
            browser.macros.delete('image')

    def test_file(self):
        browser = self.layer.get_browser(smi_settings)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            image = test_filename('test.txt')
            browser.login(user, user)
            self.assertEqual(browser.open('/root/edit'), 200)
            browser.macros.create(
                'Silva File', id='file', title='Text File', file=image)
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'file'])

            # The user should by the last author on the content and container.
            content = self.root
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.file
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['file'].click(),
                200)
            self.assertEqual(browser.url, '/root/file/edit/tab_edit')
            self.assertEqual(browser.inspect.breadcrumbs, ['root', 'Text File'])
            browser.inspect.breadcrumbs['root'].click()
            browser.macros.delete('file')

    def test_find(self):
        browser = self.layer.get_browser(smi_settings)

        for user in ['manager', 'chiefeditor', 'editor']:
            browser.login(user, user)
            self.assertEqual(browser.open('/root/edit'), 200)
            browser.macros.create(
                'Silva Find', id='search', title='Search')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'search'])

            # The user should by the last author on the content and container.
            content = self.root
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.search
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['search'].click(),
                200)
            self.assertEqual(browser.url, '/root/search/edit/tab_edit')
            self.assertEqual(browser.inspect.breadcrumbs, ['root', 'Search'])
            browser.inspect.breadcrumbs['root'].click()
            browser.macros.delete('search')

    def test_ghost(self):
        browser = self.layer.get_browser(smi_settings)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            self.assertEqual(browser.open('/root/edit'), 200)
            browser.macros.create(
                'Silva Ghost',
                id='ghost', haunted=get_content_id(self.root.index))
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'ghost'])

            # The user should by the last author on the content and container.
            content = self.root
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.ghost
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['ghost'].click(),
                200)
            self.assertEqual(browser.url, '/root/ghost/edit/tab_edit')
            self.assertEqual(browser.inspect.breadcrumbs, ['root', 'ghost'])
            form = browser.get_form('editform')
            self.assertEqual(
                form.get_control('editform.action.cancel').click(), 200)
            browser.macros.delete('ghost')

    def test_indexer(self):
        browser = self.layer.get_browser(smi_settings)

        for user in ['manager', 'chiefeditor', 'editor']:
            browser.login(user, user)
            self.assertEqual(browser.open('/root/edit'), 200)
            browser.macros.create(
                'Silva Indexer', id='indexes', title='Indexes')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'indexes'])

            # The user should by the last author on the content and container.
            content = self.root
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.indexes
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit form
            self.assertEqual(
                browser.inspect.folder_listing['indexes'].click(), 200)
            self.assertEqual(browser.url, '/root/indexes/edit/tab_edit')
            self.assertEqual(browser.inspect.breadcrumbs, ['root', 'Indexes'])
            form = browser.get_form('form')
            self.assertEqual(
                form.get_control('form.action.cancel').click(), 200)
            browser.macros.delete('indexes')

    def test_link(self):
        browser = self.layer.get_browser(smi_settings)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            self.assertEqual(browser.open('/root/edit'), 200)
            browser.macros.create(
                'Silva Link',
                id='infrae', title='Infrae', url='http://infrae.com')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'infrae'])

            # The user should by the last author on the content and container.
            content = self.root
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.infrae
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit form
            self.assertEqual(
                browser.inspect.folder_listing['infrae'].click(), 200)
            self.assertEqual(browser.url, '/root/infrae/edit/tab_edit')
            self.assertEqual(browser.inspect.breadcrumbs, ['root', 'infrae'])
            form = browser.get_form('editform')
            self.assertEqual(
                form.get_control('editform.action.cancel').click(), 200)
            browser.macros.delete('infrae')

    def test_autotoc(self):
        browser = self.layer.get_browser(smi_settings)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            self.assertEqual(browser.open('/root/edit'), 200)
            browser.macros.create(
                'Silva AutoTOC', id='sitemap', title='Sitemap')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'sitemap'])

            # The user should by the last author on the content and container.
            content = self.root
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.sitemap
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit form
            self.assertEqual(
                browser.inspect.folder_listing['sitemap'].click(), 200)
            self.assertEqual(browser.url, '/root/sitemap/edit/tab_edit')
            self.assertEqual(browser.inspect.breadcrumbs, ['root', 'Sitemap'])
            form = browser.get_form('editform')
            self.assertEqual(
                form.get_control('editform.action.cancel').click(), 200)
            browser.macros.delete('sitemap')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentCreationTestCase))
    return suite

# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings
from Products.Silva.tests.helpers import test_filename
from silva.core.references.reference import get_content_id


class ContentInFolderTestCase(unittest.TestCase):
    """For each role make each content in a folder.
    """
    layer = FunctionalLayer
    container = 'Silva Folder'

    def setUp(self):
        self.root = self.layer.get_application()

    def test_document(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            self.container,
            id='container', title='First Container', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Container'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Document', id='documentation', title='Documentation')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'documentation'])

            # The user should by the last author on the content and container.
            content = self.root.container
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.container.documentation
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['documentation'].click(), 200)
            self.assertEqual(
                browser.url, '/root/container/documentation/edit/tab_edit')
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'First Container', 'documentation'])
            browser.inspect.breadcrumbs['First Container'].click()

            browser.macros.delete('documentation')

        browser.login('manager', 'manager')
        self.assertEqual(
            browser.inspect.breadcrumbs,
            ['root', 'First Container'])
        self.assertEqual(browser.inspect.breadcrumbs['root'].click(), 200)
        browser.macros.delete('container')

    def test_folder(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            self.container,
            id='container', title='First Container', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Container'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Folder',
                id='folder', title='Second Folder', default_item='Silva Document')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'folder'])

            # The user should by the last author on the content and container.
            content = self.root.container
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.container.folder
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['folder'].click(),
                200)
            self.assertEqual(
                browser.url, '/root/container/folder/edit/tab_edit')
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'First Container', 'Second Folder'])
            browser.inspect.breadcrumbs['First Container'].click()

            browser.macros.delete('folder')

        browser.login('manager', 'manager')
        self.assertEqual(
            browser.inspect.breadcrumbs,
            ['root', 'First Container'])
        self.assertEqual(browser.inspect.breadcrumbs['root'].click(), 200)
        browser.macros.delete('container')

    def test_publication(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            self.container,
            id='container', title='First Container', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Container'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Publication',
                id='publication', title='Second Publication', default_item='Silva Document')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'publication'])

            # The user should by the last author on the content and container.
            content = self.root.container
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.container.publication
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['publication'].click(),
                200)
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'First Container', 'Second Publication'])
            browser.inspect.breadcrumbs['First Container'].click()

            browser.macros.delete('publication')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.breadcrumbs['root'].click(), 200)
        browser.macros.delete('container')

    def test_image(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            self.container,
            id='container', title='First Container', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Container'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            image = test_filename('torvald.jpg')
            browser.login(user, user)
            browser.macros.create(
                'Silva Image', id='image', title='Torvald', file=image)
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'image'])

            # The user should by the last author on the content and container.
            content = self.root.container
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.container.image
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['image'].click(), 200)
            self.assertEqual(
                browser.url, '/root/container/image/edit/tab_edit')
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'First Container', 'Torvald'])
            browser.inspect.breadcrumbs['First Container'].click()

            browser.macros.delete('image')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.breadcrumbs['root'].click(), 200)
        browser.macros.delete('container')

    def test_file(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            self.container,
            id='container', title='First Container', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Container'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            image = test_filename('test.txt')
            browser.login(user, user)
            browser.macros.create(
                'Silva File', id='file', title='Text File', file=image)
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'file'])

            # The user should by the last author on the content and container.
            content = self.root.container
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.container.file
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['file'].click(),
                200)
            self.assertEqual(
                browser.url, '/root/container/file/edit/tab_edit')
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'First Container', 'Text File'])
            browser.inspect.breadcrumbs['First Container'].click()

            browser.macros.delete('file')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.breadcrumbs['root'].click(), 200)
        browser.macros.delete('container')

    def test_find(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            self.container,
            id='container', title='First Container', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Container'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Find', id='search', title='Search')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'search'])

            # The user should by the last author on the content and container.
            content = self.root.container
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.container.search
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['search'].click(),
                200)
            self.assertEqual(
                browser.url, '/root/container/search/edit/tab_edit')
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'First Container', 'Search'])
            browser.inspect.breadcrumbs['First Container'].click()

            browser.macros.delete('search')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.breadcrumbs['root'].click(), 200)
        browser.macros.delete('container')

    def test_ghost(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            self.container,
            id='container', title='First Container', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Container'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Ghost',
                id='ghost', haunted=get_content_id(self.root.index))
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'ghost'])

            # The user should by the last author on the content and container.
            content = self.root.container
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.container.ghost
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit page
            self.assertEqual(
                browser.inspect.folder_listing['ghost'].click(),
                200)
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'First Container', 'ghost'])
            form = browser.get_form('editform')
            self.assertEqual(
                form.get_control('editform.action.cancel').click(), 200)

            browser.macros.delete('ghost')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.breadcrumbs['root'].click(), 200)
        browser.macros.delete('container')

    def test_indexer(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            self.container,
            id='container', title='First Container', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Container'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Indexer', id='indexes', title='Indexes')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'indexes'])

            # The user should by the last author on the content and container.
            content = self.root.container
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.container.indexes
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit form
            self.assertEqual(
                browser.inspect.folder_listing['indexes'].click(), 200)
            self.assertEqual(
                browser.url, '/root/container/indexes/edit/tab_edit')
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'First Container', 'Indexes'])
            form = browser.get_form('form')
            self.assertEqual(
                form.get_control('form.action.cancel').click(), 200)

            browser.macros.delete('indexes')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.breadcrumbs['root'].click(), 200)
        browser.macros.delete('container')

    def test_link(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            self.container,
            id='container', title='First Container', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Container'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            browser.macros.create(
                'Silva Link',
                id='infrae', title='Infrae', url='http://infrae.com')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'infrae'])

            # The user should by the last author on the content and container.
            content = self.root.container
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.container.infrae
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit form
            self.assertEqual(
                browser.inspect.folder_listing['infrae'].click(), 200)
            self.assertEqual(
                browser.url, '/root/container/infrae/edit/tab_edit')
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'First Container', 'infrae'])
            form = browser.get_form('editform')
            self.assertEqual(
                form.get_control('editform.action.cancel').click(), 200)

            browser.macros.delete('infrae')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.breadcrumbs['root'].click(), 200)
        browser.macros.delete('container')

    def test_autotoc(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            self.container,
            id='container', title='First Container', default_item='Silva Document')

        self.assertEqual(
            browser.inspect.navigation['First Container'].click(), 200)

        for user in ['manager', 'chiefeditor', 'editor', 'author']:
            browser.login(user, user)
            browser.macros.create(
                'Silva AutoTOC', id='sitemap', title='Sitemap')
            self.assertEqual(
                browser.inspect.folder_listing, ['index', 'sitemap'])

            # The user should by the last author on the content and container.
            content = self.root.container
            self.assertEqual(content.sec_get_last_author_info().userid(), user)
            content = self.root.container.sitemap
            self.assertEqual(content.sec_get_last_author_info().userid(), user)

            # Visit the edit form
            self.assertEqual(
                browser.inspect.folder_listing['sitemap'].click(), 200)
            self.assertEqual(
                browser.url, '/root/container/sitemap/edit/tab_edit')
            self.assertEqual(
                browser.inspect.breadcrumbs,
                ['root', 'First Container', 'Sitemap'])
            form = browser.get_form('editform')
            self.assertEqual(
                form.get_control('editform.action.cancel').click(), 200)

            browser.macros.delete('sitemap')

        browser.login('manager', 'manager')
        self.assertEqual(browser.inspect.breadcrumbs['root'].click(), 200)
        browser.macros.delete('container')


class ContentInPublicationTestCase(ContentInFolderTestCase):
    """For each role make each content in a folder.
    """
    container = 'Silva Publication'


def test_suite():
    suite = unittest.TestSuite()
    #suite.addTest(unittest.makeSuite(ContentInFolderTestCase))
    #suite.addTest(unittest.makeSuite(ContentInPublicationTestCase))
    return suite

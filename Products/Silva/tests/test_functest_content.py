# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings
from Products.Silva.tests.helpers import test_filename
from silva.core.references.reference import get_content_id


class AuthorContentTestCase(unittest.TestCase):
    """For each role make each content in a folder.
    """
    layer = FunctionalLayer
    username = 'author'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_folder(self):
        """We should be able to add/remove a folder.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.username, self.username)

        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Folder',
            id='folder',
            title='Second Folder',
            default_item='Silva Document')
        self.assertEqual(
            browser.inspect.folder_listing, ['index', 'folder'])

        # The user should by the last author on the content and container.
        self.assertEqual(
            self.root.sec_get_last_author_info().userid(),
            self.username)
        self.assertEqual(
            self.root.folder.sec_get_last_author_info().userid(),
            self.username)

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

    def test_indexer(self):
        """Indexer should not be available.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.username, self.username)

        self.assertEqual(browser.open('/root/edit'), 200)

        form = browser.get_form('md.container')
        self.assertFalse(
            'Silva Indexer' in
            form.controls['md.container.field.content'].options)

        self.assertEqual(browser.open('/root/edit/+/Silva Indexer'), 401)

    def test_publication(self):
        """Publication should not be available either.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.username, self.username)

        self.assertEqual(browser.open('/root/edit'), 200)

        form = browser.get_form('md.container')
        self.assertFalse(
            'Silva Indexer' in
            form.controls['md.container.field.content'].options)

        self.assertEqual(browser.open('/root/edit/+/Silva Publication'), 401)

    def test_image(self):
        """Test create / edit / remove an image.
        """
        browser = self.layer.get_web_browser(smi_settings)

        image = test_filename('torvald.jpg')
        browser.login(self.username, self.username)
        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Image', id='image', title='Torvald', file=image)
        self.assertEqual(
            browser.inspect.folder_listing, ['index', 'image'])

        # The user should by the last author on the content and container.
        self.assertEqual(
            self.root.sec_get_last_author_info().userid(),
            self.username)
        self.assertEqual(
            self.root.image.sec_get_last_author_info().userid(),
            self.username)

        # Visit the edit page
        self.assertEqual(
            browser.inspect.folder_listing['image'].click(),
            200)
        self.assertEqual(browser.location, '/root/image/edit/tab_edit')

        # Change title
        form = browser.get_form('silvaObjects')
        self.assertEqual(
            form.get_control('field_image_title').value,
            'Torvald')
        form.get_control('field_image_title').value = u'Picture of Torvald'
        form.get_control('submit:method').click()
        self.assertEqual(browser.inspect.feedback, ['Changes saved.'])

        # Change format
        form = browser.get_form('editform.scaling')
        self.assertEqual(form.get_control('field_web_format').value, 'JPEG')
        form.get_control('field_web_format').value = 'PNG'
        form.get_control('scale_submit:method').click()
        self.assertEqual(
            browser.inspect.feedback,
            ['Scaling and/or format changed.'])

        # Change scaling
        form = browser.get_form('editform.scaling')
        form.get_control('field_web_scaling').value = '100x200'
        form.get_control('scale_submit:method').click()
        self.assertEqual(
            browser.inspect.feedback,
            ['Scaling and/or format changed.'])

        # Change image
        form = browser.get_form('editform.upload')
        form.get_control('field_file').value = image
        form.get_control('upload_submit:method').click()
        self.assertEqual(
            browser.inspect.feedback,
            ['Image updated.'])

        self.assertEqual(
            browser.inspect.breadcrumbs,
            ['root', 'Picture of Torvald'])
        browser.inspect.breadcrumbs['root'].click()
        browser.macros.delete('image')

    def test_file(self):
        """Test create/remove a file.
        """
        browser = self.layer.get_web_browser(smi_settings)

        image = test_filename('test.txt')
        browser.login(self.username, self.username)
        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva File', id='file', title='Text File', file=image)
        self.assertEqual(
            browser.inspect.folder_listing, ['index', 'file'])

        # The user should by the last author on the content and container.
        self.assertEqual(
            self.root.sec_get_last_author_info().userid(),
            self.username)
        self.assertEqual(
            self.root.file.sec_get_last_author_info().userid(),
            self.username)

        # Visit the edit page
        self.assertEqual(
            browser.inspect.folder_listing['file'].click(),
            200)
        self.assertEqual(browser.url, '/root/file/edit/tab_edit')
        self.assertEqual(browser.inspect.breadcrumbs, ['root', 'Text File'])
        browser.inspect.breadcrumbs['root'].click()
        browser.macros.delete('file')

    def test_ghost(self):
        """Test create / remove a ghost.
        """
        browser = self.layer.get_web_browser(smi_settings)

        browser.login(self.username, self.username)
        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Ghost',
            id='ghost', haunted=get_content_id(self.root.index))
        self.assertEqual(
            browser.inspect.folder_listing, ['index', 'ghost'])

        # The user should by the last author on the content and container.
        self.assertEqual(
            self.root.sec_get_last_author_info().userid(),
            self.username)
        self.assertEqual(
            self.root.ghost.sec_get_last_author_info().userid(),
            self.username)

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

    def test_link(self):
        """Test / create remove a link.
        """
        browser = self.layer.get_web_browser(smi_settings)

        browser.login(self.username, self.username)
        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Link',
            id='infrae', title='Infrae', url='http://infrae.com')
        self.assertEqual(
            browser.inspect.folder_listing, ['index', 'infrae'])

        # The user should by the last author on the content and container.
        self.assertEqual(
            self.root.sec_get_last_author_info().userid(),
            self.username)
        self.assertEqual(
            self.root.infrae.sec_get_last_author_info().userid(),
            self.username)

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
        """Test create/remove an autotoc.
        """
        browser = self.layer.get_web_browser(smi_settings)

        browser.login(self.username, self.username)
        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva AutoTOC', id='sitemap', title='Sitemap')
        self.assertEqual(
            browser.inspect.folder_listing, ['index', 'sitemap'])

        # The user should by the last author on the content and container.
        self.assertEqual(
            self.root.sec_get_last_author_info().userid(),
            self.username)
        self.assertEqual(
            self.root.sitemap.sec_get_last_author_info().userid(),
            self.username)

        # Visit the edit form
        self.assertEqual(
            browser.inspect.folder_listing['sitemap'].click(), 200)
        self.assertEqual(browser.url, '/root/sitemap/edit/tab_edit')
        self.assertEqual(browser.inspect.breadcrumbs, ['root', 'Sitemap'])
        form = browser.get_form('editform')
        self.assertEqual(
            form.get_control('editform.action.cancel').click(), 200)
        browser.macros.delete('sitemap')


class EditorContentTestCase(AuthorContentTestCase):
    """Test creating content as Editor.
    """
    username = 'editor'

    def test_indexer(self):
        """Test create/remove an indexer.
        """
        browser = self.layer.get_web_browser(smi_settings)

        browser.login(self.username, self.username)
        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Indexer', id='indexes', title='Indexes')
        self.assertEqual(
            browser.inspect.folder_listing, ['index', 'indexes'])

        # The user should by the last author on the content and container.
        self.assertEqual(
            self.root.sec_get_last_author_info().userid(),
            self.username)
        self.assertEqual(
            self.root.indexes.sec_get_last_author_info().userid(),
            self.username)

        # Visit the edit form
        self.assertEqual(
            browser.inspect.folder_listing['indexes'].click(), 200)
        self.assertEqual(browser.url, '/root/indexes/edit/tab_edit')
        self.assertEqual(browser.inspect.breadcrumbs, ['root', 'Indexes'])
        form = browser.get_form('form')
        self.assertEqual(
            form.get_control('form.action.cancel').click(), 200)
        browser.macros.delete('indexes')

    def test_publication(self):
        """Test create / remove a publication.
        """
        browser = self.layer.get_web_browser(smi_settings)

        browser.login(self.username, self.username)
        self.assertEqual(browser.open('/root/edit'), 200)
        browser.macros.create(
            'Silva Publication',
            id='publication',
            title='Second Publication',
            default_item='Silva Document')
        self.assertEqual(
            browser.inspect.folder_listing, ['index', 'publication'])

        # The user should by the last author on the content and container.
        self.assertEqual(
            self.root.sec_get_last_author_info().userid(),
            self.username)
        self.assertEqual(
            self.root.publication.sec_get_last_author_info().userid(),
            self.username)

        # Visit the edit page
        self.assertEqual(
            browser.inspect.folder_listing['publication'].click(),
            200)
        self.assertEqual(
            browser.inspect.breadcrumbs,
            ['root', 'Second Publication'])
        browser.inspect.breadcrumbs['root'].click()
        browser.macros.delete('publication')


class ChiefEditorContentTestCase(EditorContentTestCase):
    """Test creating content as ChiefEditor.
    """
    username = 'chiefeditor'


class ManagerContentTestCase(ChiefEditorContentTestCase):
    """Test creating content as Manager.
    """
    username = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    #suite.addTest(unittest.makeSuite(AuthorContentTestCase))
    #suite.addTest(unittest.makeSuite(EditorContentTestCase))
    #suite.addTest(unittest.makeSuite(ChiefEditorContentTestCase))
    #suite.addTest(unittest.makeSuite(ManagerContentTestCase))
    return suite

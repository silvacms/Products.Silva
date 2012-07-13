# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings
from silva.core.references.reference import get_content_id


class BaseTest(unittest.TestCase):

    layer = FunctionalLayer

    def setUp(self):
        """
            Set up objects for test :

            + root (Silva root)
                |
                + folder (Silva Folder)
                    |
                    +- folderdoc (Silva Document)
                    |
                    +- pub (Silva Publication)
                        |
                        +- pubdoc (Silva Document)
        """
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.folder = getattr(self.root, 'folder')

        factory = self.folder.manage_addProduct['Silva']
        factory.manage_addPublication('pub', 'Publication')
        self.publication = getattr(self.folder, 'pub')

        factory = self.folder.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('folderdoc', 'Document inside `folder`')
        self.folderdoc = getattr(self.folder, 'folderdoc')

        factory = self.publication.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('pubdoc', 'Document inside `pub`')
        self.pubdoc = getattr(self.publication, 'pubdoc')

        self.layer.logout()
        self.browser = self.layer.get_web_browser(smi_settings)
        self.browser.login('manager', 'manager')


class TestAddGhostFolder(BaseTest):
    """ Test add form for ghost folder
    """

    def goto_add_form(self):
        self.assertEqual(self.browser.open('/root/edit'), 200)

        form = self.browser.get_form('md.container')
        form.get_control('md.container.field.content').value = 'Silva Ghost Folder'
        self.assertEqual(form.submit('md.container.action.new'), 200)
        self.assertEqual(self.browser.url, '/root/edit/+/Silva Ghost Folder')

        return self.browser.get_form('addform')

    def test_add_form_save(self):
        form = self.goto_add_form()

        publication_id = get_content_id(self.publication)
        form.get_control('addform.field.id').value = 'ghostfolder'
        form.get_control('addform.field.haunted').value = publication_id
        self.assertEqual(form.submit(name="addform.action.save"), 200)

        self.assertTrue('ghostfolder' in self.root.objectIds())
        self.assertEqual(
            self.browser.inspect.feedback, ['Added Silva Ghost Folder.'])
        self.assertEqual(self.browser.url, '/root/edit')

    def test_add_form_save_and_edit(self):
        form = self.goto_add_form()

        publication_id = get_content_id(self.publication)
        form.get_control('addform.field.id').value = 'ghostfolder'
        form.get_control('addform.field.haunted').value = publication_id
        self.assertEqual(form.submit(name="addform.action.save_edit"), 200)

        self.assertTrue('ghostfolder' in self.root.objectIds())
        self.assertEqual(
            self.browser.inspect.feedback, ['Added Silva Ghost Folder.'])
        self.assertEqual(self.browser.url, '/root/ghostfolder/edit')

    def test_cancel(self):
        form = self.goto_add_form()

        publication_id = get_content_id(self.publication)
        form.get_control('addform.field.id').value = 'ghostfolder'
        form.get_control('addform.field.haunted').value = publication_id
        self.assertEqual(form.submit(name="addform.action.cancel"), 200)

        self.assertTrue('ghostfolder' not in self.root.objectIds())
        self.assertEqual(self.browser.inspect.feedback, [])
        self.assertEqual(self.browser.url, '/root/edit')


class TestEditGhostFolder(BaseTest):
    """ test ghost folder edit form
    """
    def setUp(self):
        super(TestEditGhostFolder, self).setUp()

        self.layer.login('editor')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost_folder', "Ghost folder on root/folder",
            haunted=self.folder)
        self.ghost_folder = getattr(self.root, 'ghost_folder')
        self.layer.logout()

    def goto_form(self):
        path = "/".join(self.ghost_folder.getPhysicalPath())
        self.assertEqual(self.browser.open(path + '/edit'), 200)
        return self.browser.get_form("editform")

    def test_edit_form_reference_field(self):
        form = self.goto_form()
        reference_field = form.get_control("editform.field.haunted")
        self.assertEqual(
            reference_field.value,
            str(get_content_id(self.folder)),
            "reference field value should be the intid of the folder")

    def test_edit_form_set_new_haunted(self):
        form = self.goto_form()

        publication_id = get_content_id(self.publication)
        form.get_control("editform.field.haunted").value = publication_id
        self.assertEqual(form.submit(name="editform.action.save-changes"), 200)

        self.assertEqual(self.browser.inspect.feedback, ['Changes saved.'])
        self.assertEqual(self.publication, self.ghost_folder.get_haunted())

    def test_sync(self):
        form = self.goto_form()
        self.assertEqual(form.submit(name="editform.action.synchronize"), 200)
        self.assertEqual(
            self.browser.inspect.feedback, ['Ghost Folder synchronized'])

        self.assertEqual(['folderdoc', 'pub'], self.ghost_folder.objectIds())

        self.assertEqual(
            "Silva Ghost Folder", self.ghost_folder['pub'].meta_type)
        self.assertEqual(
            "Silva Ghost", self.ghost_folder['folderdoc'].meta_type)

        pubghost = self.ghost_folder['pub']
        self.assertEquals(['pubdoc'], pubghost.objectIds())
        self.assertEquals('Silva Ghost', pubghost['pubdoc'].meta_type)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAddGhostFolder))
    suite.addTest(unittest.makeSuite(TestEditGhostFolder))
    return suite

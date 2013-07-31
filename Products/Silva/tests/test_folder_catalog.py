# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import FunctionalLayer, CatalogTransaction


class FolderCatalogTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Data Folder')

    def search(self, **kwargs):
        return map(lambda b: (b.getPath(), b.publication_status),
                   self.root.service_catalog(**kwargs))

    def test_unapproved(self):
        """If a folder doesn't have an index it is unapproved in the
        catalog.
        """
        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/folder', 'unapproved')])

    def test_add_public(self):
        """A folder is public in the catalog if it is_published (have
        an index).
        """
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/folder', 'public'),
             ('/root/folder/index', 'public')])

    def test_add_public_transaction(self):
        """A folder is public in the catalog if it is_published (have
        an index) within a transaction.
        """
        with CatalogTransaction():
            factory = self.root.folder.manage_addProduct['Silva']
            factory.manage_addAutoTOC('index', 'Index')

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/folder', 'public'),
             ('/root/folder/index', 'public')])

    def test_rename(self):
        """A renamed folder is reindexed.
        """
        self.root.manage_renameObject('folder', 'renamed_folder')

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/renamed_folder', 'unapproved')])

    def test_rename_transaction(self):
        """A renamed folder is reindexed within a transaction.
        """
        with CatalogTransaction():
            self.root.manage_renameObject('folder', 'renamed_folder')

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/renamed_folder', 'unapproved')])

    def test_moving(self):
        """A moved folder is reindexed.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        token = self.root.manage_cutObjects(['folder'])
        self.root.publication.manage_pasteObjects(token)

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/publication', 'unapproved'),
             ('/root/publication/folder', 'unapproved')])

    def test_moving_transaction(self):
        """A moved folder is reindexed with a transaction.
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('publication', 'Publication')
            token = self.root.manage_cutObjects(['folder'])
            self.root.publication.manage_pasteObjects(token)

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/publication', 'unapproved'),
             ('/root/publication/folder', 'unapproved')])

    def test_copy(self):
        """A copy of a folder is indexed.
        """
        token = self.root.manage_copyObjects(['folder'])
        self.root.manage_pasteObjects(token)

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/folder', 'unapproved'),
             ('/root/copy_of_folder', 'unapproved')])

    def test_copy_transaction(self):
        """A copy of a folder is indexed within a transaction.
        """
        with CatalogTransaction():
            token = self.root.manage_copyObjects(['folder'])
            self.root.manage_pasteObjects(token)

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/folder', 'unapproved'),
             ('/root/copy_of_folder', 'unapproved')])

    def test_deletion(self):
        """A removed folder is no longer cataloged.
        """
        self.root.manage_delObjects(['folder'])
        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved')])

    def test_deletion_transaction(self):
        """A removed folder is no longer cataloged within a transaction.
        """
        with CatalogTransaction():
            self.root.manage_delObjects(['folder'])

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved')])

    def test_add_deletion_transaction(self):
        """Add an remove a folder The catalog content should not change.
        """
        with CatalogTransaction():
            factory = self.root.folder.manage_addProduct['Silva']
            factory.manage_addAutoTOC('index', 'Index')
            self.root.folder.manage_delObjects(['index'])

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/folder', 'unapproved')])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderCatalogTestCase))
    return suite

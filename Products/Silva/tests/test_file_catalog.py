# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva import File
from Products.Silva.testing import FunctionalLayer
from Products.Silva.testing import CatalogTransaction, Transaction


class DefaultFileCatalogTestCase(unittest.TestCase):
    layer = FunctionalLayer
    implementation = None

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        if self.implementation is not None:
            self.root.service_files.storage = self.implementation

        with Transaction():
            with self.layer.open_fixture('dark_energy.txt') as data:
                factory = self.root.manage_addProduct['Silva']
                factory.manage_addFile(
                    'universe', u'Not related to Silva', data)

    def search(self, **kwargs):
        return map(lambda b: (b.getPath(), b.publication_status),
                   self.root.service_catalog(**kwargs))

    def test_fulltext(self):
        """Content and title of the file is indexed in its fulltext.
        """
        self.assertItemsEqual(
            self.search(fulltext='dark energy'),
            [('/root/universe', 'public')])
        self.assertItemsEqual(
            self.search(fulltext='silva'),
            [('/root/universe', 'public')])
        self.assertItemsEqual(
            self.search(fulltext='zope'),
            [])

    def test_replaced(self):
        """A file is replaced. The new file should still be in the
        catalog.
        """
        with Transaction():
            self.root.manage_delObjects(['universe'])
            with self.layer.open_fixture('dark_energy.txt') as data:
                factory = self.root.manage_addProduct['Silva']
                factory.manage_addFile(
                    'universe', u'It is all about updates', data)

        self.assertItemsEqual(
            self.search(fulltext='dark energy'),
            [('/root/universe', 'public')])
        self.assertItemsEqual(
            self.search(fulltext='updates'),
            [('/root/universe', 'public')])
        self.assertItemsEqual(
            self.search(fulltext='silva'),
            [])

    def test_replaced_transaction(self):
        """A file is replaced. The new file should still be in the
        catalog.
        """
        with CatalogTransaction():
            self.root.manage_delObjects(['universe'])
            with self.layer.open_fixture('dark_energy.txt') as data:
                factory = self.root.manage_addProduct['Silva']
                factory.manage_addFile(
                    'universe', u'It is all about updates', data)

        self.assertItemsEqual(
            self.search(fulltext='dark energy'),
            [('/root/universe', 'public')])
        self.assertItemsEqual(
            self.search(fulltext='updates'),
            [('/root/universe', 'public')])
        self.assertItemsEqual(
            self.search(fulltext='silva'),
            [])

    def test_rename(self):
        """A file is reindexed if it is renamed.
        """
        with Transaction():
            self.root.manage_renameObject('universe', 'renamed_universe')

        self.assertItemsEqual(
            self.search(fulltext='dark energy'),
            [('/root/renamed_universe', 'public')])
        self.assertItemsEqual(
            self.search(fulltext='in zope'),
            [])

    def test_rename_transaction(self):
        """A file is reindexed if it is renamed.
        """
        with CatalogTransaction():
            self.root.universe.set_title(u'All true in Zope')
            self.root.manage_renameObject('universe', 'renamed_universe')

        self.assertItemsEqual(
            self.search(fulltext='dark energy'),
            [('/root/renamed_universe', 'public')])
        self.assertItemsEqual(
            self.search(fulltext='in zope'),
            [('/root/renamed_universe', 'public')])

    def test_rename_title(self):
        """A file whose the title changed is reindexed.
        """
        with Transaction():
            self.root.universe.set_title(u'All true in Zope')

        self.assertItemsEqual(
            self.search(fulltext='silva'),
            [])
        self.assertItemsEqual(
            self.search(fulltext='zope'),
            [('/root/universe', 'public')])

    def test_moving(self):
        """A moved filed is reindexed.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('publication', 'Publication')
            token = self.root.manage_cutObjects(['universe'])
            self.root.publication.manage_pasteObjects(token)

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/publication', 'unapproved'),
             ('/root/publication/universe', 'public')])

    def test_moving_transaction(self):
        """A moved filed is reindexed.
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('publication', 'Publication')
            token = self.root.manage_cutObjects(['universe'])

        self.root.publication.manage_pasteObjects(token)
        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved'),
             ('/root/publication', 'unapproved'),
             ('/root/publication/universe', 'public')])

    def test_copy(self):
        """A copy of a file is indexed.
        """
        with Transaction():
            token = self.root.manage_copyObjects(['universe'])
            self.root.manage_pasteObjects(token)

        self.assertItemsEqual(
            self.search(fulltext='dark energy'),
            [('/root/universe', 'public'),
             ('/root/copy_of_universe', 'public')])

    def test_copy_transaction(self):
        """A copy of a file is indexed.
        """
        with CatalogTransaction():
            token = self.root.manage_copyObjects(['universe'])
            self.root.manage_pasteObjects(token)

        self.assertItemsEqual(
            self.search(fulltext='dark energy'),
            [('/root/universe', 'public'),
             ('/root/copy_of_universe', 'public')])

    def test_deletion(self):
        """A file is unindex when it is removed.
        """
        with Transaction():
            self.root.manage_delObjects(['universe'])

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved')])
        self.assertItemsEqual(
            self.search(fulltext='dark energy'),
            [])

    def test_deletion_transaction(self):
        """A file is unindex when it is removed.
        """
        with CatalogTransaction():
            self.root.manage_delObjects(['universe'])

        self.assertItemsEqual(
            self.search(path='/root'),
            [('/root', 'unapproved')])
        self.assertItemsEqual(
            self.search(fulltext='dark energy'),
            [])


class BlobFileCatalogTestCase(DefaultFileCatalogTestCase):
    """Test blob file implementation.
    """
    implementation = File.BlobFile


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DefaultFileCatalogTestCase))
    suite.addTest(unittest.makeSuite(BlobFileCatalogTestCase))
    return suite

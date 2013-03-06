# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import IContainerManager

from DateTime import DateTime
from Products.Silva.testing import FunctionalLayer, CatalogTransaction


class CatalogVersioningTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

    def search(self, path):
        return map(lambda b: (b.getPath(), b.publication_status),
                   self.root.service_catalog(path=path))

    def test_unapproved(self):
        """By default everything is cataloged and unapproved.
        """
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/document', 'unapproved'),
             ('/root/document/0', 'unapproved')])

    def test_approved(self):
        """If you approve a document it is recatalogued.
        """
        IPublicationWorkflow(self.root.document).approve(DateTime() + 60)
        self.assertItemsEqual(
            self.search('/root/document'),
            [('/root/document', 'approved'),
             ('/root/document/0', 'approved')])

    def test_approved_transaction(self):
        with CatalogTransaction():
            IPublicationWorkflow(self.root.document).approve(DateTime() + 60)

        self.assertItemsEqual(
            self.search('/root/document'),
            [('/root/document', 'approved'),
             ('/root/document/0', 'approved')])

    def test_publish(self):
        """If you publish a document, it is recataloged.
        """
        IPublicationWorkflow(self.root.document).publish()
        self.assertItemsEqual(
            self.search('/root/document'),
            [('/root/document', 'public'),
             ('/root/document/0', 'public')])

    def test_closed(self):
        """If you close a document, its version is no longer
        catalogued, and the document appears as unapproved.
        """
        IPublicationWorkflow(self.root.document).publish()
        IPublicationWorkflow(self.root.document).close()

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/document', 'unapproved')])

    def test_closed_transaction(self):
        """If you close a document within a transaction, its version
        is no longer catalogued, and the document appears as
        unapproved.
        """
        with CatalogTransaction():
            IPublicationWorkflow(self.root.document).publish()
            IPublicationWorkflow(self.root.document).close()

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/document', 'unapproved')])

    def test_new(self):
        """If you create a new version of a published document, it
        appears in the catalog.
        """
        IPublicationWorkflow(self.root.document).publish()
        IPublicationWorkflow(self.root.document).new_version()

        self.assertItemsEqual(
            self.search('/root/document'),
            [('/root/document', 'public'),
             ('/root/document/0', 'public'),
             ('/root/document/1', 'unapproved')])

    def test_new_transaction(self):
        """If you create a new version of a published document within
        a transaction, it appears in the catalog.
        """
        with CatalogTransaction():
            IPublicationWorkflow(self.root.document).publish()
            IPublicationWorkflow(self.root.document).new_version()

        self.assertItemsEqual(
            self.search('/root/document'),
            [('/root/document', 'public'),
             ('/root/document/0', 'public'),
             ('/root/document/1', 'unapproved')])

    def test_new_approved(self):
        IPublicationWorkflow(self.root.document).publish()
        IPublicationWorkflow(self.root.document).new_version()
        IPublicationWorkflow(self.root.document).approve(DateTime() + 60)

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/document', 'public'),
             ('/root/document/0', 'public'),
             ('/root/document/1', 'approved')])

    def test_new_published(self):
        """If we published, make a new version and publish again the
        document, it should be published.
        """
        IPublicationWorkflow(self.root.document).publish()
        IPublicationWorkflow(self.root.document).new_version()
        IPublicationWorkflow(self.root.document).publish()

        self.assertItemsEqual(
            self.search('/root/document'),
            [('/root/document', 'public'),
             ('/root/document/1', 'public')])

    def test_new_published_transaction(self):
        """If we published, make a new version and publish again the
        document, it should be published.
        """
        with CatalogTransaction():
            IPublicationWorkflow(self.root.document).publish()
            IPublicationWorkflow(self.root.document).new_version()
            IPublicationWorkflow(self.root.document).publish()

        self.assertItemsEqual(
            self.search('/root/document'),
            [('/root/document', 'public'),
             ('/root/document/1', 'public')])

    def test_rename(self):
        """Rename a published document.
        """
        IPublicationWorkflow(self.root.document).publish()
        self.root.manage_renameObject('document', 'renamed_document')
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'public'),
             ('/root/renamed_document', 'public'),
             ('/root/renamed_document/0', 'public')])

    def test_copy(self):
        """Copy a published document. The copy should be catalogued
        and not published.
        """
        IPublicationWorkflow(self.root.document).publish()
        with IContainerManager(self.root).copier() as copier:
            copier(self.root.document)

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'public'),
             ('/root/document', 'public'),
             ('/root/document/0', 'public'),
             ('/root/copy_of_document', 'unapproved')])

    def test_copy_transaction(self):
        """Copy a published document within a transaction. The copy
        should be catalogued and not published.
        """
        with CatalogTransaction():
            IPublicationWorkflow(self.root.document).publish()
            with IContainerManager(self.root).copier() as copier:
                copier(self.root.document)

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'public'),
             ('/root/document', 'public'),
             ('/root/document/0', 'public'),
             ('/root/copy_of_document', 'unapproved')])

    def test_moving(self):
        """Test moving published elements into a folder.
        """
        IPublicationWorkflow(self.root.document).publish()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        with IContainerManager(self.root.folder).mover() as mover:
            mover(self.root.document)

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'public'),
             ('/root/folder', 'public'),
             ('/root/folder/document', 'public'),
             ('/root/folder/document/0', 'public')])

    def test_moving_transaction(self):
        """Test moving published elements into a folder within a transaction.
        """
        with CatalogTransaction():
            IPublicationWorkflow(self.root.document).publish()
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')
            with IContainerManager(self.root.folder).mover() as mover:
                mover(self.root.document)

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'public'),
             ('/root/folder', 'public'),
             ('/root/folder/document', 'public'),
             ('/root/folder/document/0', 'public')])

    def test_deletion(self):
        """Test deleting a document.
        """
        self.root.manage_delObjects(['document'])
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),])

    def test_deletion_transaction(self):
        """Test deleting a document.
        """
        with CatalogTransaction():
            with IContainerManager(self.root).deleter() as deleter:
                deleter(self.root.document)

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),])

    def test_add_published_rename_transaction(self):
        """Test adding a new content, publishing it and moving it.
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('info', 'Content')
            IPublicationWorkflow(self.root.info).publish()
            with IContainerManager(self.root).renamer() as renamer:
                self.assertNotEqual(
                    renamer((self.root.info, 'renamed', 'Renamed content')),
                    None)

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'public'),
             ('/root/renamed', 'public'),
             ('/root/renamed/0', 'public'),
             ('/root/document', 'unapproved'),
             ('/root/document/0', 'unapproved')])

    def test_remove_add_publish_transaction(self):
        """Test removing a content, adding a new one with the same,
        publishing it and remove it again.
        """
        with CatalogTransaction():
            with IContainerManager(self.root).deleter() as deleter:
                deleter(self.root.document)

            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')
            IPublicationWorkflow(self.root.document).publish()

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'public'),
             ('/root/document', 'public'),
             ('/root/document/0', 'public')])

    def test_remove_add_published_remove_transaction(self):
        """Test removing a content, adding a new one with the same,
        publishing it and remove it again.
        """
        with CatalogTransaction():
            with IContainerManager(self.root).deleter() as deleter:
                deleter(self.root.document)

            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Fake')
            IPublicationWorkflow(self.root.document).publish()

            with IContainerManager(self.root).deleter() as deleter:
                deleter(self.root.document)

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved')])

    def test_add_published_remove_rename_transaction(self):
        """Test removing a content, adding a new one with the same,
        publishing it and remove it again.
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('temp', 'Temp document')
            IPublicationWorkflow(self.root.temp).publish()

            with IContainerManager(self.root).deleter() as deleter:
                deleter(self.root.document)

            with IContainerManager(self.root).renamer() as renamer:
                self.assertNotEqual(
                    renamer((self.root.temp, 'document', 'Document')),
                    None)

        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'public'),
             ('/root/document', 'public'),
             ('/root/document/0', 'public')])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CatalogVersioningTestCase))
    return suite

# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core.interfaces import IPublicationWorkflow

from DateTime import DateTime
from Products.Silva.testing import FunctionalLayer


class CatalogVersioningTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')

    def search(self, path):
        return map(lambda b: (b.getPath(), b.publication_status),
                   self.root.service_catalog(path=path))

    def test_unapproved(self):
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/document', 'unapproved'),
             ('/root/document/0', 'unapproved')])

    def test_approved(self):
        IPublicationWorkflow(self.root.document).approve(DateTime() + 60)
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/document', 'approved'),
             ('/root/document/0', 'approved')])

    def test_public(self):
        IPublicationWorkflow(self.root.document).publish()
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/document', 'public'),
             ('/root/document/0', 'public')])

    def test_closed(self):
        IPublicationWorkflow(self.root.document).publish()
        IPublicationWorkflow(self.root.document).close()
        # Close unindex the version, but the versioned is kept in the catalog
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/document', 'unapproved')])

    def test_new(self):
        IPublicationWorkflow(self.root.document).publish()
        IPublicationWorkflow(self.root.document).new_version()
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/document', 'public'),
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
        IPublicationWorkflow(self.root.document).publish()
        IPublicationWorkflow(self.root.document).new_version()
        IPublicationWorkflow(self.root.document).publish()
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/document', 'public'),
             ('/root/document/1', 'public')])

    def test_rename(self):
        """Rename a published document.
        """
        IPublicationWorkflow(self.root.document).publish()
        self.root.manage_renameObject('document', 'renamed_document')
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/renamed_document', 'public'),
             ('/root/renamed_document/0', 'public')])

    def test_copy(self):
        """Copy a published document.
        """
        IPublicationWorkflow(self.root.document).publish()
        token = self.root.manage_copyObjects(['document'])
        self.root.manage_pasteObjects(token)
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/document', 'public'),
             ('/root/document/0', 'public'),
             ('/root/copy_of_document', 'unapproved'),
             ('/root/copy_of_document/0', 'unapproved')])

    def test_moving(self):
        """Test moving published elements into a folder.
        """
        IPublicationWorkflow(self.root.document).publish()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        token = self.root.manage_cutObjects(['document'])
        self.root.folder.manage_pasteObjects(token)
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),
             ('/root/folder', 'unapproved'),
             ('/root/folder/document', 'unapproved'),
             ('/root/folder/document/0', 'unapproved')])

    def test_deletion(self):
        """Test deleting a document.
        """
        self.root.manage_delObjects(['document'])
        self.assertItemsEqual(
            self.search('/root'),
            [('/root', 'unapproved'),])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CatalogVersioningTestCase))
    return suite

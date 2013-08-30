# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.component import getUtility
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer, Transaction
from Products.SilvaMetadata.interfaces import ReadOnlyError
from silva.core.services.interfaces import IMetadataService
from silva.core.interfaces import IMember, IContainerManager, IVersionedContent


class VersioningAuthorAndCreationTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        with Transaction():
            self.root = self.layer.get_application()
            self.layer.login('editor')
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

    def test_created_information(self):
        """Test that default information is properly filled on a
        recently created versioned content.
        """
        document = self.root._getOb('document', None)
        self.assertIsNot(document, None)
        creator = document.get_creator_info()
        self.assertTrue(verifyObject(IMember, creator))
        self.assertEqual(creator.userid(), 'editor')
        author = document.get_last_author_info()
        self.assertTrue(verifyObject(IMember, author))
        self.assertEqual(author.userid(), 'editor')
        self.assertNotEqual(document.get_creation_datetime(), None)
        self.assertNotEqual(document.get_modification_datetime(), None)

        version = document.get_editable()
        self.assertIsNot(version, None)
        creator = version.get_creator_info()
        self.assertTrue(verifyObject(IMember, creator))
        self.assertEqual(creator.userid(), 'editor')
        author = version.get_last_author_info()
        self.assertTrue(verifyObject(IMember, author))
        self.assertEqual(author.userid(), 'editor')
        self.assertNotEqual(version.get_creation_datetime(), None)
        self.assertNotEqual(version.get_modification_datetime(), None)

    def test_copy_information(self):
        """Test that the information on a copy is properly
        filled. Although the document have been created by editor, the
        copy have been created by author.
        """
        with Transaction():
            self.layer.login('author')
            with IContainerManager(self.root).copier() as copier:
                copy = copier(self.root.document)

        self.assertTrue(verifyObject(IVersionedContent, copy))

        creator = copy.get_creator_info()
        self.assertTrue(verifyObject(IMember, creator))
        self.assertEqual(creator.userid(), 'author')
        author = copy.get_last_author_info()
        self.assertTrue(verifyObject(IMember, author))
        self.assertEqual(author.userid(), 'author')
        self.assertNotEqual(copy.get_creation_datetime(), None)
        self.assertNotEqual(copy.get_modification_datetime(), None)


class MetadataVersioningTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        with Transaction():
            self.root = self.layer.get_application()
            self.layer.login('editor')
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

    def test_version_metadata(self):
        """Test simple validation on the metadata system while setting
        values.
        """
        service = getUtility(IMetadataService)
        version = self.root.document.get_editable()
        binding = service.getMetadata(version)

        # Unicode
        self.assertEqual(
            binding.setValues(
                'silva-content', {'maintitle': 'UTF-8 non décodé'}),
            {})
        self.assertEqual(
            binding.get('silva-content', 'maintitle'),
            u'UTF-8 non décodé')
        self.assertEqual(
            binding.setValues(
                'silva-content', {'maintitle': u'UTF-8 décodé'}),
            {})
        self.assertEqual(
            binding.get('silva-content', 'maintitle'),
            u'UTF-8 décodé')

        # Datetime validation
        self.assertEqual(
            binding.setValues(
                'silva-extra', {'modificationtime': 'today'}),
            {'modificationtime': u'You did not enter a valid date and time.'})

        # Choice validation
        self.assertEqual(
            binding.setValues(
                'silva-settings', {'hide_from_tocs': 'maybe'}),
            {'hide_from_tocs': u'You selected an item that was not in the list.'})
        self.assertEqual(
            binding.get('silva-settings', 'hide_from_tocs'),
            'do not hide')
        self.assertEqual(
            binding.setValues(
                'silva-settings', {'hide_from_tocs': 'hide'}),
            {})
        self.assertEqual(
            binding.get('silva-settings', 'hide_from_tocs'),
            'hide')

    def test_versioned_content_metadata(self):
        """Test that you can access the metadata from the versioned
        content, but not change it.
        """
        service = getUtility(IMetadataService)

        document = self.root.document
        version = self.root.document.get_editable()

        # Now it should work, you should get the metadata of the document
        document_binding = service.getMetadata(document)
        self.assertNotEqual(document_binding, document)
        self.assertEqual(
            document_binding.get('silva-content', 'maintitle'),
            u"Document")
        self.assertEqual(
            service.getMetadataValue(document, 'silva-content', 'maintitle'),
            u"Document")

        # You can't change the value.
        with self.assertRaises(ReadOnlyError):
            document_binding.setValues('silva-content', {'maintitle': u'Ghost'})

        # Nothing changed.
        document_binding = service.getMetadata(document)
        self.assertEqual(
            document_binding.get('silva-content', 'maintitle'),
            u"Document")
        self.assertEqual(
            service.getMetadataValue(document, 'silva-content', 'maintitle'),
            u"Document")

        # Update document metadata
        version_binding = service.getMetadata(version)
        version_binding.setValues('silva-content', {'maintitle': u"Changed"})

        # You should see the values from the content point of view.
        document_binding = service.getMetadata(document)
        self.assertEqual(
            document_binding.get('silva-content', 'maintitle'),
            u"Changed")
        self.assertEqual(
            service.getMetadataValue(document, 'silva-content', 'maintitle'),
            u"Changed")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MetadataVersioningTestCase))
    suite.addTest(unittest.makeSuite(VersioningAuthorAndCreationTestCase))
    return suite

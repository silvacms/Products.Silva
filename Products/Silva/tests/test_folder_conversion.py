# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.interface import alsoProvides, noLongerProvides
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.interface.verify import verifyObject

from silva.core.interfaces import IFolder, IPublication
from silva.core.layout.interfaces import ICustomizableTag
from silva.core.services.interfaces import ICatalogService
from silva.core.interfaces import ContentError

from Products.Silva.testing import FunctionalLayer
from Products.Silva.testing import assertTriggersEvents


class IAdditionalMarker(ICustomizableTag):
    pass


class FolderConvertionTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        self.get_id = getUtility(IIntIds).register
        self.get_listing = self.root.objectIds

    def test_invalid_conversion(self):
        """Test that you can't convert a folder to a folder, a
        publication to a publication, a root to a folder or a
        publication.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addPublication('publication', 'Publication')

        with self.assertRaises(ContentError):
            self.root.folder.to_folder()
        with self.assertRaises(ContentError):
            self.root.publication.to_publication()
        with self.assertRaises(ContentError):
            self.root.to_publication()
        with self.assertRaises(ContentError):
            self.root.to_folder()

    def test_folder_to_publication(self):
        """Test Silva Folder to Silva Publication conversion.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')

        self.assertTrue('folder' in self.get_listing('Silva Folder'))
        self.assertTrue(verifyObject(IFolder, self.root.folder))
        self.assertFalse(IPublication.providedBy(self.root.folder))
        folder_id = self.get_id(self.root.folder)

        with assertTriggersEvents('ObjectModifiedEvent'):
            self.root.folder.to_publication()

        self.assertFalse('folder' in self.get_listing('Silva Folder'))
        self.assertTrue('folder' in self.get_listing('Silva Publication'))
        self.assertTrue(verifyObject(IPublication, self.root.folder))
        self.assertTrue('index' in self.root.folder.objectIds())
        self.assertEqual(folder_id, self.get_id(self.root.folder))

    def test_publication_to_folder(self):
        """Test Silva Publication to Silva Folder conversion.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')

        self.assertTrue('publication' in self.get_listing('Silva Publication'))
        self.assertTrue(verifyObject(IPublication, self.root.publication))
        publication_id = self.get_id(self.root.publication)

        with assertTriggersEvents('ObjectModifiedEvent'):
            self.root.publication.to_folder()

        self.assertFalse('publication' in self.get_listing('Silva Publication'))
        self.assertTrue('publication' in self.get_listing('Silva Folder'))
        self.assertTrue(verifyObject(IFolder, self.root.publication))
        self.assertFalse(IPublication.providedBy(self.root.publication))
        self.assertTrue('index' in self.root.publication.objectIds())
        self.assertEqual(publication_id, self.get_id(self.root.publication))

    def test_publication_to_folder_with_marker(self):
        """Test Silva Publication to Silva Folder conversion when the
        content have been provided with an interface.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')

        publication_id = self.get_id(self.root.publication)
        alsoProvides(self.root.publication, IAdditionalMarker)
        self.assertTrue('publication' in self.get_listing('Silva Publication'))
        self.assertTrue(verifyObject(IPublication, self.root.publication))

        with assertTriggersEvents('ObjectModifiedEvent'):
            self.root.publication.to_folder()

        self.assertFalse('publication' in self.get_listing('Silva Publication'))
        self.assertTrue('publication' in self.get_listing('Silva Folder'))
        self.assertTrue(verifyObject(IFolder, self.root.publication))
        self.assertFalse(IPublication.providedBy(self.root.publication))
        self.assertTrue(IAdditionalMarker.providedBy(self.root.publication))
        self.assertTrue('index' in self.root.publication.objectIds())
        self.assertEqual(publication_id, self.get_id(self.root.publication))

    def test_folder_to_publication_with_marker_past(self):
        """Test Silva Folder to Silva Publication conversion when the
        folder have been provided in the past with a marker.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')

        folder_id = self.get_id(self.root.folder)
        alsoProvides(self.root.folder, IAdditionalMarker)
        noLongerProvides(self.root.folder, IAdditionalMarker)
        self.assertTrue('folder' in self.get_listing('Silva Folder'))
        self.assertTrue(verifyObject(IFolder, self.root.folder))
        self.assertFalse(IPublication.providedBy(self.root.folder))

        with assertTriggersEvents('ObjectModifiedEvent'):
            self.root.folder.to_publication()

        self.assertFalse('folder' in self.get_listing('Silva Folder'))
        self.assertTrue('folder' in self.get_listing('Silva Publication'))
        self.assertTrue(verifyObject(IPublication, self.root.folder))
        self.assertTrue('index' in self.root.folder.objectIds())
        self.assertEqual(folder_id, self.get_id(self.root.folder))

    def test_publication_to_folder_catalog(self):
        """Verify that the catalog is updated when the conversion is done.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

        catalog = getUtility(ICatalogService)
        brains = catalog(meta_type='Silva Folder')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getObject(), self.root.folder)
        brains = catalog(meta_type='Silva Publication')
        self.assertEqual(len(brains), 0)

        with assertTriggersEvents('ObjectModifiedEvent'):
            self.root.folder.to_publication()

        brains = catalog(meta_type='Silva Folder')
        self.assertEqual(len(brains), 0)
        brains = catalog(meta_type='Silva Publication')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getObject(), self.root.folder)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderConvertionTestCase))
    return suite

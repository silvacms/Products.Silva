# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import io
import unittest
import zipfile

from silva.core import interfaces
from silva.core.interfaces import IZipFileImporter, IContentExporter
from zope.component import getAdapter
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer, TestRequest


class ZipTestCase(unittest.TestCase):
    """Test Zip import/export.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addLink(
            'link', 'Link', relative=False, url="http:/infrae.com")

    def test_zip_file_importer(self):
        """Test ZIP import adapter.
        """
        importer = IZipFileImporter(self.root.folder, None)
        self.assertTrue(verifyObject(interfaces.IZipFileImporter, importer))
        importer = IZipFileImporter(self.root.link, None)
        self.assertEqual(importer, None)

    def test_zip_file_importer_is_archive(self):
        """Test method isFullmediaArchive on an importer.
        """
        importer = IZipFileImporter(self.root.folder)
        with self.layer.open_fixture('test1.zip') as test_archive:
            self.assertEqual(importer.isFullmediaArchive(test_archive), False)
        with self.layer.open_fixture('test_import_link.zip') as test_archive:
            self.assertEqual(importer.isFullmediaArchive(test_archive), True)

    def test_zip_content_exporter(self):
        """Test ZIP content exporter.
        """
        exporter = getAdapter(self.root.folder, IContentExporter, name='zip')
        self.assertTrue(verifyObject(IContentExporter, exporter))

    def test_import_export(self):
        """Import/export a Zip file.
        """
        # XXX This test needs improvement.
        importer = interfaces.IArchiveFileImporter(self.root.folder)
        with self.layer.open_fixture('test1.zip') as test_archive:
            succeeded, failed = importer.importArchive(test_archive)
        self.assertItemsEqual(
            succeeded,
            ['testzip/Clock.swf',
             'testzip/bar/image2.jpg',
             'testzip/foo/bar/baz/image5.jpg',
             'testzip/foo/bar/image4.jpg',
             'testzip/foo/image3.jpg',
             'testzip/image1.jpg',
             'testzip/sound1.mp3'])
        self.assertItemsEqual(failed, [])

        exporter = getAdapter(self.root.folder, IContentExporter, name='zip')
        data = exporter.export(TestRequest(), stream=io.BytesIO())

        export = zipfile.ZipFile(data, 'r')
        self.assertItemsEqual(
            ['assets/1.jpg', 'assets/2.jpg', 'assets/3.jpg',
             'assets/4.jpg', 'assets/5.swf', 'assets/6.jpg',
             'assets/7.mp3', 'silva.xml'],
            export.namelist())
        export.close()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZipTestCase))
    return suite

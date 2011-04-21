# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from cStringIO import StringIO
from zipfile import ZipFile
import unittest

from silva.core import interfaces
from zope.component import getAdapter, queryAdapter
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer, TestCase
from Products.Silva.tests.helpers import open_test_file


class ZipTestCase(TestCase):
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

    def test_import_adapter(self):
        """Test ZIP import adapter.
        """
        importer = getAdapter(
            self.root.folder, interfaces.IZipFileImporter)
        self.failUnless(verifyObject(interfaces.IZipFileImporter, importer))
        importer = queryAdapter(
            self.root.link, interfaces.IZipFileImporter)
        self.assertEqual(importer, None)

    def test_import_is_archive(self):
        """Test method isFullmediaArchive on an importer.
        """
        importer = getAdapter(
            self.root.folder, interfaces.IZipFileImporter)
        with open_test_file('test1.zip') as test_archive:
            self.assertEqual(importer.isFullmediaArchive(test_archive), False)
        with open_test_file('test_import_link.zip') as test_archive:
            self.assertEqual(importer.isFullmediaArchive(test_archive), True)

    def test_export(self):
        """Import/export a Zip file.
        """
        # XXX This test needs improvement.
        zip_import = open_test_file('test1.zip')
        importer = interfaces.IArchiveFileImporter(self.root.folder)
        succeeded, failed = importer.importArchive(zip_import)
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

        exporter = getAdapter(
            self.root.folder, interfaces.IContentExporter, name='zip')
        export = StringIO(exporter.export())

        zip_export = ZipFile(export, 'r')
        self.assertItemsEqual(
            ['assets/1.jpg', 'assets/2.jpg', 'assets/3.jpg',
             'assets/4.jpg', 'assets/5.swf', 'assets/6.jpg',
             'assets/7.mp3', 'silva.xml'],
            zip_export.namelist())
        zip_export.close()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZipTestCase))
    return suite

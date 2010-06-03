# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from cStringIO import StringIO
from zipfile import ZipFile
import unittest

from silva.core import interfaces
from silva.core.interfaces.events import IContentImported
from zope.component import getAdapter
from zope.component.eventtesting import getEvents, clearEvents
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer, TestCase
from Products.Silva.tests.helpers import open_test_file


class ImportExportTripTestCase(TestCase):
    """Export/Import/Export data in XML. Check that you obtain twice
    the same export.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_round_trip(self):
        """Make a trip:
        1. Create items.
        2. Export them.
        3. Import them.
        4. Export them.
        5. Check that export created at 2. and 4. are identical.
        """
        # 1. create content
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')

        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addLink(
            'infrae', 'Infrae', relative=False, url='http://infrae.com')
        factory.manage_addIndexer('assets', 'Assets')
        factory.manage_addFolder('pictures', 'Pictures')
        factory.manage_addFolder('trash', 'Trash')

        factory = self.root.publication.pictures.manage_addProduct['Silva']
        factory.manage_addImage(
            'torvald', 'Torvald', open_test_file('torvald.jpg'))
        factory.manage_addFile(
            'unknown', 'Something testique', open_test_file('testimage.gif'))
        factory.manage_addFolder('tobesorted', 'To Be Sorted Eh!')

        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addGhost(
            'nice', None, haunted=self.root.publication.pictures.torvald)

        factory = self.root.publication.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('kikoo.py')

        # 2. export
        exporter1 = getAdapter(
            self.root.publication,
            interfaces.IContentExporter, name='zip')
        self.failUnless(verifyObject(interfaces.IContentExporter, exporter1))

        export1 = exporter1.export()

        # 3. import
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Import Folder')
        importer = getAdapter(
            self.root.folder, interfaces.IZipFileImporter)
        self.failUnless(verifyObject(interfaces.IZipFileImporter, importer))

        clearEvents()
        importer.importFromZip(StringIO(export1))

        self.assertEventsAre(
            ['ContentImported for /root/folder/publication',
             'ContentImported for /root/folder/publication/assets',
             'ContentImported for /root/folder/publication/infrae',
             'ContentImported for /root/folder/publication/kikoo.py',
             'ContentImported for /root/folder/publication/nice',
             'ContentImported for /root/folder/publication/pictures',
             'ContentImported for /root/folder/publication/pictures/tobesorted',
             'ContentImported for /root/folder/publication/pictures/torvald',
             'ContentImported for /root/folder/publication/pictures/unknown',
             'ContentImported for /root/folder/publication/trash'],
            IContentImported)

        imported_ghost = self.root.folder.publication.nice
        imported_image = self.root.folder.publication.pictures.torvald
        self.assertEqual(
            imported_ghost.get_editable().get_haunted(),
            imported_image)

        # 4. export
        exporter2 = getAdapter(
            self.root.folder.publication,
            interfaces.IContentExporter, name='zip')

        export2 = exporter2.export()

        # 5. compare the two exports
        zip_export1 = ZipFile(StringIO(export1))
        zip_export2 = ZipFile(StringIO(export2))

        self.failUnless('silva.xml' in zip_export1.namelist())
        self.assertListEqual(zip_export1.namelist(), zip_export2.namelist())
        silva_export1 = zip_export1.read('silva.xml')
        silva_export2 = zip_export2.read('silva.xml')

        self.assertXMLEqual(silva_export1, silva_export2)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ImportExportTripTestCase))
    return suite

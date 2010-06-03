# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from cStringIO import StringIO
from zipfile import ZipFile
import re
import unittest

from zope.component import getAdapter, getUtility

# Silva
from Products.Silva.silvaxml import xmlexport
from Products.Silva.silvaxml.xmlexport import ExternalReferenceError
from Products.Silva.testing import FunctionalLayer, TestCase
from Products.Silva.tests.helpers import open_test_file
from Products.SilvaMetadata.interfaces import IMetadataService
from silva.core import interfaces


DATETIME_RE = re.compile(
    r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')


class SilvaXMLTestCase(TestCase):
    """Basic TestCase to test XML export features.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def get_namespaces(self):
        # this is needed because we don't know the namespaces registered
        # with the exported.  These are dynamic and depend on the extensions
        # which are using the exporter.  This function is an attempt at
        # dynamically inserting the namespaces, and hopefully gets the
        # order correct.
        nss = []
        items = xmlexport.theXMLExporter._namespaces.items()
        items.sort()
        for prefix, uri in items:
            nss.append('xmlns:%s="%s"' % (prefix, uri))
        return ' '.join(nss)

    def get_version(self):
        return 'Silva %s' % self.root.get_silva_software_version()

    def genericize(self, string):
        return DATETIME_RE.sub(r'YYYY-MM-DDTHH:MM:SS', string)

    def assertExportEqual(self, xml, filename, globs=None):
        """Verify that the xml result of an export is the same than
        the one contained in a test file.
        """
        if globs is None:
            globs = globals()
        with open_test_file(filename, globs) as xml_file:
            expected_xml = xml_file.read().format(
                namespaces=self.get_namespaces(),
                version=self.get_version())
            actual_xml = self.genericize(xml)
            self.assertXMLEqual(expected_xml, actual_xml)


class XMLExportTestCase(SilvaXMLTestCase):
    """Test XML Exporter.
    """

    def setUp(self):
        super(XMLExportTestCase, self).setUp()
        self.root.manage_addProduct['Silva'].manage_addFolder(
            'folder', 'This is <boo>a</boo> folder',
            policy_name='Silva AutoTOC')

    def test_folder(self):
        """Export a folder.
        """
        self.root.folder.manage_addProduct['Silva'].manage_addFolder(
            'folder', 'This is &another; a subfolder',
            policy_name='Silva AutoTOC')

        xml, info = xmlexport.exportToString(self.root.folder)
        self.assertExportEqual(xml, 'test_export_folder.silvaxml')
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_fallback(self):
        """Test the fallback exporter: create a Zope 2 folder in a
        Silva folder and export it.
        """
        self.root.folder.manage_addProduct['OFS'].manage_addFolder(
            'zope2folder', 'Zope 2 Folder')

        xml, info = xmlexport.exportToString(self.root.folder)
        self.assertExportEqual(xml, 'test_export_fallback.silvaxml')
        self.assertEqual(
            info.getZexpPaths(),
            [(('', 'root', 'folder', 'zope2folder'), '1.zexp')])
        self.assertEqual(info.getAssetPaths(), [])

    def test_indexer(self):
        """Export an indexer.
        """
        self.root.folder.manage_addProduct['Silva'].manage_addIndexer(
            'indexer', 'Index of this site')

        metadata = getUtility(IMetadataService).getMetadata(
            self.root.folder.indexer)
        metadata.setValues(
            'silva-extra',
            {'content_description': 'Index the content of your website.',
             'comment': 'Nothing special is required.'})

        xml, info = xmlexport.exportToString(self.root.folder)
        self.assertExportEqual(xml, 'test_export_indexer.silvaxml')
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_ghost(self):
        """Export a ghost.
        """
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addLink(
            'link', 'New website', url='http://infrae.com/', relative=False)
        factory.manage_addGhost(
            'ghost', None, haunted=self.root.folder.link)

        xml, info = xmlexport.exportToString(self.root.folder)
        self.assertExportEqual(xml, 'test_export_ghost.silvaxml')
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_ghost_outside_of_export(self):
        """Export a ghost that link something outside of export tree.
        """
        self.root.manage_addProduct['Silva'].manage_addLink(
            'link', 'New website', url='http://infrae.com/', relative=False)
        self.root.folder.manage_addProduct['Silva'].manage_addGhost(
            'ghost', None, haunted=self.root.folder.link)

        self.assertRaises(
            ExternalReferenceError, xmlexport.exportToString, self.root.folder)

    def test_ghostfolder(self):
        """Export a ghost folder.
        """
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('container', 'Content')
        factory.manage_addGhostFolder(
            'ghost', None, haunted=self.root.folder.container)
        factory = self.root.folder.container.manage_addProduct['Silva']
        factory.manage_addLink(
            'link', 'Infrae', url='http://infrae.com', relative=False)
        factory.manage_addFile('file', 'Torvald blob')

        self.root.folder.ghost.haunt()

        xml, info = xmlexport.exportToString(self.root.folder)
        self.assertExportEqual(xml, 'test_export_ghostfolder.silvaxml')
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(
            info.getAssetPaths(),
            [(('', 'root', 'folder', 'container', 'file'), '1')])

    def test_ghostfolder_outside_of_export(self):
        """Export a ghost folder but not the ghosted folder.
        """
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('container', 'Content')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost', None, haunted=self.root.folder.container)
        factory = self.root.folder.container.manage_addProduct['Silva']
        factory.manage_addLink(
            'link', 'Infrae', url='http://infrae.com', relative=False)
        factory.manage_addFile('file', 'Torvald blob')

        self.root.ghost.haunt()

        self.assertRaises(
            ExternalReferenceError, xmlexport.exportToString, self.root.ghost)

    def test_link_relative(self):
        """Export a link with to an another Silva object.
        """
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFile('file', 'Torvald file')
        factory.manage_addFolder('new', 'New changes')
        factory = self.root.folder.new.manage_addProduct['Silva']
        factory.manage_addLink(
            'link', 'Last file',
            relative=True, target=self.root.folder.file)

        xml, info = xmlexport.exportToString(self.root.folder)
        self.assertExportEqual(xml, 'test_export_link.silvaxml')
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(
            info.getAssetPaths(),
            [(('', 'root', 'folder', 'file'), '1')])

    def test_link_relative_outside_of_export(self):
        """Export a link with to an another Silva object.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFile('file', 'Torvald file')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addLink(
            'link', 'Last file', relative=True, target=self.root.file)

        self.assertRaises(
            ExternalReferenceError, xmlexport.exportToString, self.root.folder)


class ZipTestCase(TestCase):
    """Test Zip import/export.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_zip_export(self):
        """Import/export a Zip file.
        """
        # XXX This test needs improvement.
        self.root.manage_addProduct['Silva'].manage_addFolder(
            'folder', 'Folder')

        zip_import = open_test_file('test1.zip')
        importer = interfaces.IArchiveFileImporter(self.root.folder)
        succeeded, failed = importer.importArchive(zip_import)
        self.assertListEqual(
            succeeded,
            ['testzip/Clock.swf', 'testzip/bar/image2.jpg',
             'testzip/foo/bar/baz/image5.jpg', 'testzip/foo/bar/image4.jpg',
             'testzip/foo/image3.jpg', 'testzip/image1.jpg',
             'testzip/sound1.mp3'])
        self.assertListEqual(failed, [])

        exporter = getAdapter(
            self.root.folder, interfaces.IContentExporter, name='zip')
        export = StringIO(exporter.export())

        zip_export = ZipFile(export, 'r')
        self.assertListEqual(
            ['assets/1.jpg', 'assets/2.jpg', 'assets/3.jpg',
             'assets/4.jpg', 'assets/5.swf', 'assets/6.jpg',
             'assets/7.mp3', 'silva.xml'],
            zip_export.namelist())
        zip_export.close()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZipTestCase))
    suite.addTest(unittest.makeSuite(XMLExportTestCase))
    return suite

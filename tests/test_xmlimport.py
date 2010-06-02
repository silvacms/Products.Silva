# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from StringIO import StringIO
from zipfile import ZipFile
import unittest

from DateTime import DateTime

from zope.component import getUtility
from zope.component.eventtesting import getEvents, clearEvents
from silva.core import interfaces
from silva.core.interfaces.events import IContentImported

from Products.Silva.silvaxml import xmlimport
from Products.Silva.tests import SilvaTestCase
from Products.Silva.testing import FunctionalLayer, TestCase
from Products.Silva.tests.helpers import open_test_file
from Products.SilvaMetadata.interfaces import IMetadataService


class SilvaXMLTestCase(TestCase):
    """Test case with some helpers to work with XML import.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.metadata = getUtility(IMetadataService)
        # setUp triggered some events. Clear them.
        clearEvents()

    def import_file(self, filename, globs=None, replace=False):
        """Import an XML file.
        """
        if globs is None:
            globs = globals()
        with open_test_file(filename, globs) as source_file:
            xmlimport.importFromFile(
                source_file, self.root.folder, replace=replace)

    def import_zip(self, filename, globs=None, replace=False):
        """Import a ZIP file.
        """
        if globs is None:
            globs = globals()
        with open_test_file(filename, globs) as source_file:
            source_zip = ZipFile(source_file)
            info = xmlimport.ImportInfo()
            info.setZIPFile(source_zip)
            import_file = StringIO(source_zip.read('silva.xml'))
            xmlimport.importFromFile(
                import_file, self.root.folder, info=info, replace=replace)

    def assertEventsAre(self, expected, interface=IContentImported):
        triggered = map(repr_event, getEvents(interface))
        self.assertListEqual(triggered, expected)


def repr_event(evt):
    """Represent an event as a string.
    """
    return '%s for %s' % (
        evt.__class__.__name__, '/'.join(evt.object.getPhysicalPath()))


class XMLImportTestCase(SilvaXMLTestCase):
    """Import data from an XML file.
    """

    def test_publication(self):
        """Test import of publication.
        """
        self.import_file('test_import_publication.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder/publication',
             'ContentImported for /root/folder/publication/index'])
        self.assertListEqual(self.root.folder.objectIds(), ['publication'])

        publication = self.root.folder.publication
        binding = self.metadata.getMetadata(publication)

        self.failUnless(interfaces.IPublication.providedBy(publication))
        self.assertEquals(publication.get_title(), u'Test Publication')
        self.assertEquals(binding.get('silva-extra', 'creator'), u'admin')
        self.assertEquals(
            binding.get('silva-content', 'maintitle'), u'Test Publication')

    def test_folder(self):
        """Test folder import.
        """
        self.import_file('test_import_folder.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder/folder',
             'ContentImported for /root/folder/folder/subfolder'])
        self.assertListEqual(self.root.folder.objectIds(), ['folder'])
        self.assertListEqual(self.root.folder.folder.objectIds(), ['subfolder'])

        folder = self.root.folder.folder
        binding = self.metadata.getMetadata(folder)

        self.failUnless(interfaces.IFolder.providedBy(folder))
        self.assertEquals(folder.get_title(), u'Test Folder')
        self.assertEquals(binding.get('silva-extra', 'creator'), u'admin')
        self.assertEquals(binding.get('silva-extra', 'lastauthor'), u'admin')
        self.assertEquals(
            binding.get('silva-extra', 'contactname'), u'Henri McArthur')
        self.assertEquals(
            binding.get('silva-extra', 'content_description'),
            u'This folder have been created only in testing purpose.')
        self.assertEquals(
            binding.get('silva-content', 'maintitle'), u'Test Folder')

        subfolder = folder.subfolder
        binding = self.metadata.getMetadata(subfolder)

        self.assertEquals(subfolder.get_title(), u'Second test folder')
        self.assertEquals(binding.get('silva-extra', 'creator'), u'henri')
        self.assertEquals(binding.get('silva-extra', 'lastauthor'), u'henri')

    def test_link_to_file(self):
        """Import a link that is linked to a file.
        """
        self.import_zip('test_import_link.zip')
        self.assertEventsAre(
            ['ContentImported for /root/folder/folder',
             'ContentImported for /root/folder/folder/file',
             'ContentImported for /root/folder/folder/index',
             'ContentImported for /root/folder/folder/new',
             'ContentImported for /root/folder/folder/new/link'])
        self.assertListEqual(self.root.folder.objectIds(), ['folder'])
        self.assertListEqual(
            self.root.folder.folder.objectIds(),
            ['file', 'index', 'new'])
        self.assertListEqual(
            self.root.folder.folder.new.objectIds(),
            ['link'])

        link = self.root.folder.folder.new.link
        datafile = self.root.folder.folder.file

        self.failUnless(interfaces.ILink.providedBy(link))
        self.failUnless(interfaces.IFile.providedBy(datafile))
        self.assertEquals(datafile.get_title(),  u'Torvald file')

        version = link.get_editable()
        self.failIf(version is None)
        self.assertEqual(link.get_viewable(), None)
        self.assertEqual(version.get_title(), u'Last file')
        self.assertEquals(
            DateTime('2004-04-23T16:13:39Z'),
            version.get_modification_datetime())

        binding = self.metadata.getMetadata(version)
        self.assertEquals(binding.get('silva-extra', 'creator'), u'henri')
        self.assertEquals(binding.get('silva-extra', 'lastauthor'), u'henri')
        self.assertEquals(
            binding.get('silva-extra', 'content_description'),
            u'Link to the lastest file.')

        self.assertEquals(version.get_relative(), True)
        self.assertEquals(version.get_target(), datafile)

        binding = self.metadata.getMetadata(datafile)
        self.assertEquals(binding.get('silva-extra', 'creator'), u'pauline')
        self.assertEquals(binding.get('silva-extra', 'lastauthor'), u'pauline')
        self.assertEquals(
            binding.get('silva-extra', 'comment'),
            u'This file contains Torvald lastest whereabouts.')

    def test_link_url(self):
        """Import a link set with an URL.
        """
        self.import_file('test_import_link.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder/folder',
             'ContentImported for /root/folder/folder/index',
             'ContentImported for /root/folder/folder/link'])
        self.assertListEqual(self.root.folder.objectIds(), ['folder'])
        self.assertListEqual(
            self.root.folder.folder.objectIds(),
            ['index', 'link'])

        link = self.root.folder.folder.link

        version = link.get_viewable()
        self.failIf(version is None)
        self.assertEqual(link.get_editable(), None)
        self.assertEqual(version.get_title(), u'Best website')

        binding = self.metadata.getMetadata(version)
        self.assertEquals(binding.get('silva-extra', 'creator'), u'wimbou')
        self.assertEquals(binding.get('silva-extra', 'lastauthor'), u'wimbou')
        self.assertEquals(
            binding.get('silva-extra', 'content_description'),
            u'Best website in the world.')

        self.assertEquals(version.get_relative(), False)
        self.assertEquals(version.get_url(), 'http://wimbou.be')

    def test_ghost_to_image(self):
        """Import a ghost to an image.
        """
        self.import_zip('test_import_ghost.zip')
        self.assertEventsAre(
            ['ContentImported for /root/folder/folder',
             'ContentImported for /root/folder/folder/images',
             'ContentImported for /root/folder/folder/images/ghost_of_torvald_jpg',
             'ContentImported for /root/folder/folder/torvald_jpg'])
        self.assertListEqual(self.root.folder.objectIds(), ['folder'])
        self.assertListEqual(
            self.root.folder.folder.objectIds(),
            ['images', 'torvald_jpg'])
        self.assertListEqual(
            self.root.folder.folder.images.objectIds(),
            ['ghost_of_torvald_jpg'])

        image = self.root.folder.folder.torvald_jpg
        ghost = self.root.folder.folder.images.ghost_of_torvald_jpg
        self.failUnless(interfaces.IImage.providedBy(image))
        self.failUnless(interfaces.IGhostContent.providedBy(ghost))

        version = ghost.get_viewable()
        self.failIf(version is None)
        self.assertEqual(ghost.get_editable(), None)
        self.assertEqual(version.get_title(), u'Torvald picture')
        self.assertEqual(image.get_title(), u'Torvald picture')
        self.assertEqual(version.get_haunted(), image)

        binding = self.metadata.getMetadata(image)
        self.assertEquals(binding.get('silva-extra', 'creator'), u'pauline')
        self.assertEquals(binding.get('silva-extra', 'lastauthor'), u'pauline')
        self.assertEquals(
            binding.get('silva-extra', 'comment'),
            u'Torvald public face.')

    def test_indexer(self):
        """Import an indexer.
        """
        self.import_file('test_import_indexer.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder/folder',
             'ContentImported for /root/folder/folder/indexer'])
        self.assertListEqual(self.root.folder.objectIds(), ['folder'])
        self.assertListEqual(self.root.folder.folder.objectIds(), ['indexer'])

        indexer = self.root.folder.folder.indexer
        self.failUnless(interfaces.IIndexer.providedBy(indexer))
        self.assertEqual(indexer.get_title(), u'Index of this site')

        binding = self.metadata.getMetadata(indexer)
        self.assertEquals(binding.get('silva-extra', 'creator'), u'antoine')
        self.assertEquals(binding.get('silva-extra', 'lastauthor'), u'antoine')
        self.assertEquals(
            binding.get('silva-extra', 'comment'),
            u'Nothing special is required.')
        self.assertEquals(
            binding.get('silva-extra', 'content_description'),
            u'Index the content of your website.')

    def test_ghost_folder(self):
        """Import a ghost folder that contains various things.
        """
        self.import_file('test_import_ghostfolder.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder/folder',
             'ContentImported for /root/folder/folder/container',
             'ContentImported for /root/folder/folder/container/indexer',
             'ContentImported for /root/folder/folder/container/link',
             'ContentImported for /root/folder/folder/ghost'])
        self.assertListEqual(self.root.folder.objectIds(), ['folder'])
        self.assertListEqual(
            self.root.folder.folder.objectIds(),
            ['container', 'ghost'])
        self.assertListEqual(
            self.root.folder.folder.container.objectIds(),
            ['indexer', 'link'])

        folder = self.root.folder.folder.ghost
        container = self.root.folder.folder.container
        self.failUnless(interfaces.IGhostFolder.providedBy(folder))
        self.assertEqual(folder.get_haunted(), container)
        self.assertListEqual(folder.objectIds(), container.objectIds())


class SetTestCase(SilvaTestCase.SilvaTestCase):


    def test_autotoc_import(self):
        source_file = open_test_file('test_autotoc.xml')
        xmlimport.importFromFile(
            source_file,
            self.root)
        source_file.close()

        autotoc = self.root.autotokkies
        self.assertEquals(
            'Autotoc 1',
            autotoc.get_title())
        self.assertEquals(
            'Silva AutoTOC',
            autotoc.meta_type)

    def test_metadata_import(self):
        # this is a reproduction of the xmlimport bug
        # which causes import to fail if an installed metadata set is not
        # present in the import
        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        source_file = open_test_file('test_metadata_import.xml')
        xmlimport.importFromFile(
            source_file, importfolder)
        source_file.close()
        linkversion = importfolder.testfolder.testfolder2.test_link.get_editable()
        metadata_service = linkversion.service_metadata
        binding = metadata_service.getMetadata(linkversion)
        self.assertEquals(
           'the short title of the testlink',
            binding._getData(
                'silva-content').data['shorttitle'])

    def test_replace_objects(self):
        source_file = open_test_file('test_autotoc.xml')
        xmlimport.importFromFile(
            source_file,
            self.root)
        source_file.close()

        autotoc = self.root.autotokkies
        self.assertEquals(
            'Autotoc 1',
            autotoc.get_title())
        self.assertEquals(
            'Silva AutoTOC',
            autotoc.meta_type)

        source_file = open_test_file('test_autotoc2.xml')
        xmlimport.importReplaceFromFile(
            source_file,
            self.root)
        source_file.close()

        autotoc = self.root.autotokkies
        self.assertEquals(
            'Autotoc 2',
            autotoc.get_title())
        self.assertEquals(
            'Silva AutoTOC',
            autotoc.meta_type)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLImportTestCase))
    suite.addTest(unittest.makeSuite(SetTestCase))
    return suite

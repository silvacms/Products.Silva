# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from StringIO import StringIO
from zipfile import ZipFile
import unittest

from DateTime import DateTime

from zope.component import getUtility
from zope.component.eventtesting import clearEvents
from silva.core import interfaces
from silva.core.interfaces.events import IContentImported

from Products.Silva.silvaxml import xmlimport
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
                source_file, self.root, replace=replace)

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
                import_file, self.root, info=info, replace=replace)


class XMLImportTestCase(SilvaXMLTestCase):
    """Import data from an XML file.
    """

    def test_publication(self):
        """Test import of publication.
        """
        self.import_file('test_import_publication.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/publication',
             'ContentImported for /root/publication/index'],
            IContentImported)

        publication = self.root.publication
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
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/subfolder'],
            IContentImported)
        self.assertListEqual(self.root.folder.objectIds(), ['subfolder'])

        folder = self.root.folder
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
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/file',
             'ContentImported for /root/folder/index',
             'ContentImported for /root/folder/new',
             'ContentImported for /root/folder/new/link'],
            IContentImported)
        self.assertListEqual(
            self.root.folder.objectIds(),
            ['file', 'index', 'new'])
        self.assertListEqual(
            self.root.folder.new.objectIds(),
            ['link'])

        link = self.root.folder.new.link
        datafile = self.root.folder.file

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
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/index',
             'ContentImported for /root/folder/link'],
            IContentImported)
        self.assertListEqual(
            self.root.folder.objectIds(),
            ['index', 'link'])

        link = self.root.folder.link

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

    def test_broken_metadata(self):
        """Import a file that refer to unknown metadata set and
        elements.
        """
        self.import_file('test_import_metadata.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/publication'],
            IContentImported)

        publication = self.root.publication
        self.failUnless(interfaces.IPublication.providedBy(publication))

    def test_fallback(self):
        """Import an archive that contain a ZEXP.
        """
        self.import_zip('test_import_fallback.zip')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/zope2folder'],
            IContentImported)
        folder = self.root.folder
        self.assertEquals(folder.get_title(), u"Stuff's container")
        self.assertEquals(folder.objectIds(), ['zope2folder'])
        self.assertEquals(folder.zope2folder.meta_type, 'Folder')

    def test_fallback_existing(self):
        """Import an archive that contain a ZEXP with an object that
        already exists.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Existing folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('zope2folder', 'Existing Zope 2 Stuff')
        factory.manage_addIndexer('indexer', 'Index Zope 2 Stuff')

        self.import_zip('test_import_fallback.zip')
        self.assertEventsAre(
            ['ContentImported for /root/import_of_folder',
             'ContentImported for /root/import_of_folder/zope2folder'],
            IContentImported)

        folder = self.root.import_of_folder
        self.assertEquals(folder.get_title(), u"Stuff's container")
        self.assertEquals(folder.objectIds(), ['zope2folder'])
        self.assertEquals(folder.zope2folder.meta_type, 'Folder')

    def test_fallback_existing_replace(self):
        """Import an archive that contain a ZEXP with an object that
        already exists.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Existing folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('zope2folder', 'Existing Zope 2 Stuff')
        factory.manage_addIndexer('indexer', 'Index Zope 2 Stuff')

        self.import_zip('test_import_fallback.zip', replace=True)
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/zope2folder'],
            IContentImported)

        folder = self.root.folder
        self.assertEquals(folder.get_title(), u"Stuff's container")
        self.assertEquals(folder.objectIds(), ['zope2folder'])
        self.assertEquals(folder.zope2folder.meta_type, 'Folder')

    def test_ghost_to_image(self):
        """Import a ghost to an image.
        """
        self.import_zip('test_import_ghost.zip')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/images',
             'ContentImported for /root/folder/images/ghost_of_torvald_jpg',
             'ContentImported for /root/folder/torvald_jpg'],
            IContentImported)
        self.assertListEqual(
            self.root.folder.objectIds(),
            ['images', 'torvald_jpg'])
        self.assertListEqual(
            self.root.folder.images.objectIds(),
            ['ghost_of_torvald_jpg'])

        image = self.root.folder.torvald_jpg
        ghost = self.root.folder.images.ghost_of_torvald_jpg
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
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/indexer'],
            IContentImported)
        self.assertListEqual(self.root.folder.objectIds(), ['indexer'])

        indexer = self.root.folder.indexer
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
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/container',
             'ContentImported for /root/folder/container/indexer',
             'ContentImported for /root/folder/container/link',
             'ContentImported for /root/folder/ghost'],
            IContentImported)
        self.assertListEqual(
            self.root.folder.objectIds(), ['container', 'ghost'])
        self.assertListEqual(
            self.root.folder.container.objectIds(), ['indexer', 'link'])

        folder = self.root.folder.ghost
        container = self.root.folder.container
        self.failUnless(interfaces.IGhostFolder.providedBy(folder))
        self.assertEqual(folder.get_haunted(), container)
        self.assertListEqual(folder.objectIds(), container.objectIds())

    def test_autotoc(self):
        """Import some autotoc.
        """
        self.import_file('test_import_autotoc.silvaxml')
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/assets',
             'ContentImported for /root/folder/index'],
            IContentImported)
        self.assertListEqual(self.root.folder.objectIds(), ['assets', 'index'])

        assets = self.root.folder.assets
        containers = self.root.folder.index
        self.failUnless(interfaces.IAutoTOC.providedBy(assets))
        self.failUnless(interfaces.IAutoTOC.providedBy(containers))
        self.assertEqual(assets.get_title(), u'Local assets')
        self.assertEqual(containers.get_title(), u'Containers')

        self.assertEqual(assets.show_icon(), True)
        self.assertEqual(containers.show_icon(), False)
        self.assertEqual(assets.toc_depth(), -1)
        self.assertEqual(containers.toc_depth(), 42)
        self.assertListEqual(
            assets.get_local_types(),
            [u'Silva File', u'Silva Image'])
        self.assertListEqual(
            containers.get_local_types(),
            [u'Silva Folder', u'Silva Publication'])

        binding = self.metadata.getMetadata(assets)
        self.assertEqual(
            binding.get('silva-extra', 'creator'), u'hacker-kun')
        self.assertEqual(
            binding.get('silva-extra', 'lastauthor'), u'hacker-kun')
        self.assertEqual(
            binding.get('silva-extra', 'hide_from_tocs'),
            u'do not hide')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'Report local assets.')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLImportTestCase))
    return suite

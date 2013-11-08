# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from DateTime import DateTime
from Acquisition import aq_chain

from zope.component import getUtility
from zope.component.eventtesting import clearEvents, getEvents

from silva.core import interfaces
from silva.core.interfaces.events import IContentImported
from silva.core.xml import Importer, ZipImporter

from Products.Silva.testing import FunctionalLayer, TestRequest
from Products.Silva.testing import TestCase
from Products.SilvaMetadata.interfaces import IMetadataService


class SilvaXMLTestCase(TestCase):
    """Test case with some helpers to work with XML import.
    """
    layer = FunctionalLayer
    maxDiff = None

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        self.metadata = getUtility(IMetadataService)

    def assertImportFile(self, filename, imported, replace=False, update=False,
                         ignore_top_level=False):
        """Import an XML file.
        """
        clearEvents()
        request = TestRequest()
        importer = Importer(self.root, request, {
                'replace_content': replace,
                'update_content': update,
                'ignore_top_level_content': ignore_top_level})
        with self.layer.open_fixture(filename) as source:
            importer.importStream(source)
        self.assertItemsEqual(
            map(lambda event:  '/'.join(event.object.getPhysicalPath()),
                getEvents(IContentImported)),
            imported)
        return importer

    def assertImportZip(self, filename, imported, replace=False, update=False,
                        ignore_top_level=False):
        """Import a ZIP file.
        """
        clearEvents()
        request = TestRequest()
        importer = ZipImporter(self.root, request, {
                'replace_content': replace,
                'update_content': update,
                'ignore_top_level_content': ignore_top_level})
        with self.layer.open_fixture(filename) as source:
            importer.importStream(source)
        self.assertItemsEqual(
            map(lambda event:  '/'.join(event.object.getPhysicalPath()),
                getEvents(IContentImported)),
            imported)
        return importer


class XMLImportTestCase(SilvaXMLTestCase):
    """Import data from an XML file.
    """

    def test_publication(self):
        """Test import of publication.
        """
        importer = self.assertImportFile(
            'test_import_publication.silvaxml',
            ['/root/publication',
             '/root/publication/index'])
        self.assertEqual(importer.getProblems(), [])

        publication = self.root.publication
        binding = self.metadata.getMetadata(publication)

        self.assertTrue(interfaces.IPublication.providedBy(publication))
        self.assertEqual(publication.get_title(), u'Test Publication')
        self.assertEqual(
            binding.get('silva-content', 'maintitle'), u'Test Publication')

    def test_folder(self):
        """Test folder import.
        """
        importer = self.assertImportFile(
            'test_import_folder.silvaxml',
            ['/root/folder',
             '/root/folder/subfolder'])
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(self.root.folder.objectIds(), ['subfolder'])

        folder = self.root.folder
        binding = self.metadata.getMetadata(folder)

        self.assertTrue(interfaces.IFolder.providedBy(folder))
        self.assertEqual(folder.get_title(), u'Test Folder')
        self.assertEqual(
            binding.get('silva-extra', 'contactname'), u'Henri McArthur')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'This folder have been created only in testing purpose.')
        self.assertEqual(
            binding.get('silva-content', 'maintitle'), u'Test Folder')

        subfolder = folder.subfolder
        self.assertEqual(subfolder.get_title(), u'Second test folder')

    def test_folder_update(self):
        """Test folder import over an existing folder, with update on.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Existing folder')
        folder = self.root.folder
        binding = self.metadata.getMetadata(folder)

        self.assertTrue(interfaces.IFolder.providedBy(folder))
        self.assertItemsEqual(self.root.folder.objectIds(), [])
        self.assertEqual(folder.get_title(), u'Existing folder')
        self.assertEqual(binding.get('silva-extra', 'contactname'), u'')
        self.assertEqual(
            binding.get('silva-content', 'maintitle'),
            u'Existing folder')

        # We now import with update on
        importer = self.assertImportFile(
            'test_import_folder.silvaxml',
            ['/root/folder',
             '/root/folder/subfolder'],
            update=True)
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(self.root.folder.objectIds(), ['subfolder'])

        folder = self.root.folder
        binding = self.metadata.getMetadata(folder)

        self.assertTrue(interfaces.IFolder.providedBy(folder))
        self.assertEqual(folder.get_title(), u'Test Folder')
        self.assertEqual(
            binding.get('silva-extra', 'contactname'),
            u'Henri McArthur')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'This folder have been created only in testing purpose.')
        self.assertEqual(
            binding.get('silva-content', 'maintitle'),
            u'Test Folder')

        subfolder = folder.subfolder
        self.assertEqual(subfolder.get_title(), u'Second test folder')

    def test_ignore_top_level_content(self):
        """Import a container with items without creating the container.
        """
        importer = self.assertImportZip(
            'test_import_link.zip',
            ['/root/file',
             '/root/index',
             '/root/new',
             '/root/new/link'], ignore_top_level=True)
        self.assertEqual(importer.getProblems(), [])

        index = self.root.index
        link = self.root.new.link
        datafile = self.root.file

        self.assertTrue(interfaces.IAutoTOC.providedBy(index))
        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))

        self.assertEqual(self.root.get_title(), u'root')
        self.assertEqual(index.get_title_editable(), u'Imported Index')
        self.assertEqual(datafile.get_title_editable(),  u'Torvald file')
        self.assertEqual(link.get_viewable(), None)
        self.assertEqual(link.get_title_editable(), u'Last file')
        self.assertEqual(
            DateTime('2004-04-23T16:13:39Z'),
            link.get_modification_datetime())

    def test_ignore_top_level_content_existing_rename(self):
        """Import a container with data without the container, but
        some items with the same ids already exists in the import
        folder. The new items get imported under a different id.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('index', 'Existing Index')
        importer = self.assertImportZip(
            'test_import_link.zip',
            ['/root/file',
             '/root/import_of_index',
             '/root/new',
             '/root/new/link'], ignore_top_level=True)
        self.assertEqual(importer.getProblems(), [])

        index = self.root.index
        new_index = self.root.import_of_index
        link = self.root.new.link
        datafile = self.root.file

        self.assertFalse(interfaces.IAutoTOC.providedBy(index))
        self.assertTrue(interfaces.IAutoTOC.providedBy(new_index))
        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))

        self.assertEqual(self.root.get_title(), u'root')
        self.assertEqual(index.get_title_editable(), u'Existing Index')
        self.assertEqual(new_index.get_title_editable(), u'Imported Index')
        self.assertEqual(datafile.get_title(),  u'Torvald file')
        self.assertEqual(link.get_viewable(), None)
        self.assertEqual(link.get_title_editable(), u'Last file')
        self.assertEqual(
            DateTime('2004-04-23T16:13:39Z'),
            link.get_modification_datetime())

    def test_ignore_top_level_content_existing_replace(self):
        """Import a container with data without the container, but
        some items with the same ids already exists in the import
        folder. We replace the existing items.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('index', 'Existing Index')
        importer = self.assertImportZip(
            'test_import_link.zip',
            ['/root/file',
             '/root/index',
             '/root/new',
             '/root/new/link'], ignore_top_level=True, replace=True)
        self.assertEqual(importer.getProblems(), [])

        index = self.root.index
        link = self.root.new.link
        datafile = self.root.file

        self.assertTrue(interfaces.IAutoTOC.providedBy(index))
        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))

        self.assertEqual(self.root.get_title(), u'root')
        self.assertEqual(index.get_title_editable(), u'Imported Index')
        self.assertEqual(datafile.get_title(),  u'Torvald file')
        self.assertEqual(link.get_viewable(), None)
        self.assertEqual(link.get_title_editable(), u'Last file')
        self.assertEqual(
            DateTime('2004-04-23T16:13:39Z'),
            link.get_modification_datetime())

    def test_ignore_top_level_content_existing_update(self):
        """Import a container with data without the container, but
        some items with the same ids already exists in the import
        folder. We update the existing items.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Existing Index')
        importer = self.assertImportZip(
            'test_import_link.zip',
            ['/root/file',
             '/root/index',
             '/root/new',
             '/root/new/link'], ignore_top_level=True, update=True)
        self.assertEqual(importer.getProblems(), [])

        index = self.root.index
        link = self.root.new.link
        datafile = self.root.file

        self.assertTrue(interfaces.IAutoTOC.providedBy(index))
        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))

        self.assertEqual(self.root.get_title(), u'root')
        self.assertEqual(index.get_title_editable(), u'Imported Index')
        self.assertEqual(datafile.get_title(),  u'Torvald file')
        self.assertEqual(link.get_viewable(), None)
        self.assertEqual(link.get_title_editable(), u'Last file')
        self.assertEqual(
            DateTime('2004-04-23T16:13:39Z'),
            link.get_modification_datetime())

    def test_ignore_top_level_content_existing_update_incompatible(self):
        """Import a container with data without the container, but
        some items with the same ids already exists in the import
        folder. We can't update the items so we recreate them under a
        different id.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('index', 'Existing Index')
        importer = self.assertImportZip(
            'test_import_link.zip',
            ['/root/file',
             '/root/import_of_index',
             '/root/new',
             '/root/new/link'], ignore_top_level=True, update=True)
        self.assertEqual(importer.getProblems(), [])

        index = self.root.index
        new_index = self.root.import_of_index
        link = self.root.new.link
        datafile = self.root.file

        self.assertFalse(interfaces.IAutoTOC.providedBy(index))
        self.assertTrue(interfaces.IAutoTOC.providedBy(new_index))
        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))

        self.assertEqual(self.root.get_title(), u'root')
        self.assertEqual(index.get_title_editable(), u'Existing Index')
        self.assertEqual(new_index.get_title_editable(), u'Imported Index')
        self.assertEqual(datafile.get_title(),  u'Torvald file')
        self.assertEqual(link.get_viewable(), None)
        self.assertEqual(link.get_title_editable(), u'Last file')
        self.assertEqual(
            DateTime('2004-04-23T16:13:39Z'),
            link.get_modification_datetime())

    def test_link_to_file(self):
        """Import a link that is linked to a file.
        """
        importer = self.assertImportZip(
            'test_import_link.zip',
            ['/root/folder',
             '/root/folder/file',
             '/root/folder/index',
             '/root/folder/new',
             '/root/folder/new/link'])
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['file', 'index', 'new'])
        self.assertItemsEqual(
            self.root.folder.new.objectIds(),
            ['link'])

        link = self.root.folder.new.link
        datafile = self.root.folder.file

        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))
        self.assertEqual(datafile.get_title(),  u'Torvald file')

        version = link.get_editable()
        self.assertFalse(version is None)
        self.assertEqual(link.get_viewable(), None)
        self.assertEqual(version.get_title(), u'Last file')
        self.assertEqual(
            DateTime('2004-04-23T16:13:39Z'),
            version.get_modification_datetime())

        binding = self.metadata.getMetadata(version)
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'Link to the lastest file.')

        self.assertEqual(version.get_relative(), True)
        self.assertEqual(version.get_target(), datafile)
        self.assertEqual(aq_chain(version.get_target()), aq_chain(datafile))

        binding = self.metadata.getMetadata(datafile)
        self.assertEqual(
            binding.get('silva-extra', 'comment'),
            u'This file contains Torvald lastest whereabouts.')

    def test_link_to_file_existing_replace(self):
        """Import a link to file in a folder that already exists. It
        replace the ids, it doesn't check if the types are the same.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        importer = self.assertImportZip(
            'test_import_link.zip',
            ['/root/folder',
             '/root/folder/file',
             '/root/folder/index',
             '/root/folder/new',
             '/root/folder/new/link'],
            replace=True)
        self.assertEqual(importer.getProblems(), [])
        self.assertTrue(interfaces.IFolder.providedBy(self.root.folder))
        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['file', 'index', 'new'])
        self.assertItemsEqual(
            self.root.folder.new.objectIds(),
            ['link'])

        link = self.root.folder.new.link
        datafile = self.root.folder.file

        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))
        self.assertEqual(datafile.get_title(),  u'Torvald file')

        version = link.get_editable()
        self.assertEqual(version.get_relative(), True)
        self.assertEqual(version.get_target(), datafile)
        self.assertEqual(aq_chain(version.get_target()), aq_chain(datafile))

    def test_link_to_file_update(self):
        """Import a link that is linked to a file.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Existing folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('new', 'Existing new folder')
        factory = self.root.folder.new.manage_addProduct['Silva']
        factory.manage_addLink('link', 'Link to Silva', url='http://silvacms.org')

        importer = self.assertImportZip(
            'test_import_link.zip',
            ['/root/folder',
             '/root/folder/file',
             '/root/folder/index',
             '/root/folder/new',
             '/root/folder/new/link'],
            update=True)
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['file', 'index', 'new'])
        self.assertItemsEqual(
            self.root.folder.new.objectIds(),
            ['link'])

        link = self.root.folder.new.link
        datafile = self.root.folder.file

        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))
        self.assertEqual(datafile.get_title(),  u'Torvald file')

        version = link.get_editable()
        self.assertFalse(version is None)
        self.assertEqual(link.get_viewable(), None)
        self.assertEqual(version.get_title(), u'Last file')
        self.assertEqual(
            DateTime('2004-04-23T16:13:39Z'),
            version.get_modification_datetime())

        binding = self.metadata.getMetadata(version)
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'Link to the lastest file.')

        self.assertEqual(version.get_relative(), True)
        self.assertEqual(version.get_target(), datafile)
        self.assertEqual(aq_chain(version.get_target()), aq_chain(datafile))

        binding = self.metadata.getMetadata(datafile)
        self.assertEqual(
            binding.get('silva-extra', 'comment'),
            u'This file contains Torvald lastest whereabouts.')

    def test_link_to_file_existing_rename(self):
        """Import a link to file in a folder that already exists. The
        imported folder should be done under a different name.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        indexer = self.root.folder
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        importer = self.assertImportZip(
            'test_import_link.zip',
            ['/root/import_of_folder',
             '/root/import_of_folder/file',
             '/root/import_of_folder/index',
             '/root/import_of_folder/new',
             '/root/import_of_folder/new/link'])
        self.assertEqual(importer.getProblems(), [])
        self.assertTrue(
            interfaces.IFolder.providedBy(self.root.import_of_folder))
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))
        self.assertEqual(indexer, self.root.folder)
        self.assertItemsEqual(
            self.root.import_of_folder.objectIds(),
            ['file', 'index', 'new'])
        self.assertItemsEqual(
            self.root.import_of_folder.new.objectIds(),
            ['link'])

        link = self.root.import_of_folder.new.link
        datafile = self.root.import_of_folder.file

        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))
        self.assertEqual(datafile.get_title(),  u'Torvald file')

        version = link.get_editable()
        self.assertEqual(version.get_relative(), True)
        self.assertEqual(version.get_target(), datafile)
        self.assertEqual(aq_chain(version.get_target()), aq_chain(datafile))

    def test_link_to_file_existing_rename_twice(self):
        """Import a link to file in a folder that already exists two times. The
        imported folder should be done under a different name for each import.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        importer = self.assertImportZip(
            'test_import_link.zip',
            ['/root/import_of_folder',
             '/root/import_of_folder/file',
             '/root/import_of_folder/index',
             '/root/import_of_folder/new',
             '/root/import_of_folder/new/link'])
        self.assertEqual(importer.getProblems(), [])
        self.assertTrue(
            interfaces.IFolder.providedBy(self.root.import_of_folder))
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        importer = self.assertImportZip(
            'test_import_link.zip',
            ['/root/import2_of_folder',
             '/root/import2_of_folder/file',
             '/root/import2_of_folder/index',
             '/root/import2_of_folder/new',
             '/root/import2_of_folder/new/link'])
        self.assertEqual(importer.getProblems(), [])
        self.assertTrue(
            interfaces.IFolder.providedBy(self.root.import2_of_folder))
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        link = self.root.import_of_folder.new.link
        datafile = self.root.import_of_folder.file

        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IFile.providedBy(datafile))
        self.assertEqual(datafile.get_title(),  u'Torvald file')

        version = link.get_editable()
        self.assertEqual(version.get_relative(), True)
        self.assertEqual(version.get_target(), datafile)
        self.assertEqual(aq_chain(version.get_target()), aq_chain(datafile))

        link2 = self.root.import2_of_folder.new.link
        datafile2 = self.root.import2_of_folder.file

        self.assertTrue(interfaces.ILink.providedBy(link2))
        self.assertTrue(interfaces.IFile.providedBy(datafile2))
        self.assertEqual(datafile2.get_title(),  u'Torvald file')

        version2 = link2.get_editable()
        self.assertEqual(version2.get_relative(), True)
        self.assertEqual(version2.get_target(), datafile2)
        self.assertEqual(aq_chain(version2.get_target()), aq_chain(datafile2))

    def test_link_url(self):
        """Import a link set with an URL.
        """
        importer = self.assertImportFile(
            'test_import_link.silvaxml',
            ['/root/folder',
             '/root/folder/index',
             '/root/folder/link'])
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['index', 'link'])

        link = self.root.folder.link

        version = link.get_viewable()
        self.assertFalse(version is None)
        self.assertEqual(link.get_editable(), None)
        self.assertEqual(version.get_title(), u'Best website')

        binding = self.metadata.getMetadata(version)
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'Best website in the world.')

        self.assertEqual(version.get_relative(), False)
        self.assertEqual(version.get_url(), 'http://wimbou.be')

    def test_broken_metadata(self):
        """Import a file that refer to unknown metadata set and
        elements.
        """
        importer = self.assertImportFile(
            'test_import_metadata.silvaxml',
            ['/root/publication'])
        self.assertEqual(importer.getProblems(), [])

        publication = self.root.publication
        self.assertTrue(interfaces.IPublication.providedBy(publication))

    def test_broken_references(self):
        """Import a file with broken references.
        """
        importer = self.assertImportFile(
            'test_import_broken_references.silvaxml',
            ['/root/folder',
             '/root/folder/ghost',
             '/root/folder/link'])

        ghost_version = self.root.folder.ghost.get_editable()
        self.assertNotEqual(ghost_version, None)
        self.assertEqual(ghost_version.get_haunted(), None)
        self.assertNotEqual(ghost_version.get_link_status(), None)

        link_version = self.root.folder.link.get_editable()
        self.assertNotEqual(link_version, None)
        self.assertEqual(link_version.get_relative(), True)
        self.assertEqual(link_version.get_target(), None)

        self.assertEqual(
            importer.getProblems(),
            [('Missing relative link target.', link_version),
             (u'Missing ghost target.', ghost_version)])

    def test_broken_workflow(self):
        """Import a link that have an invalid workflow declaration.
        """
        importer = self.assertImportFile(
            'test_import_broken_workflow.silvaxml',
            ['/root/folder',
             '/root/folder/index',
             '/root/folder/link'])
        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['index', 'link'])
        link = self.root.folder.link
        self.assertEqual(
            importer.getProblems(),
            [(u'Missing workflow information for version 0.', link)])

        self.assertFalse(link.is_published())
        self.assertIs(link.get_viewable(), None)
        self.assertIs(link.get_editable(), None)

        version = link.get_previewable()
        self.assertIsNot(version, None)
        self.assertEqual(version.get_title(), u'Best website')

    def test_fallback(self):
        """Import an archive that contain a ZEXP.
        """
        importer = self.assertImportZip(
            'test_import_fallback.zip',
            ['/root/folder',
             '/root/folder/zope2folder'])
        self.assertEqual(importer.getProblems(), [])

        folder = self.root.folder
        self.assertEqual(folder.get_title(), u"Stuff's container")
        self.assertEqual(folder.objectIds(), ['zope2folder'])
        self.assertEqual(folder.zope2folder.meta_type, 'Folder')

    def test_fallback_existing(self):
        """Import an archive that contain a ZEXP with an object that
        already exists.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Existing folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('zope2folder', 'Existing Zope 2 Stuff')
        factory.manage_addIndexer('indexer', 'Index Zope 2 Stuff')

        importer = self.assertImportZip(
            'test_import_fallback.zip',
            ['/root/import_of_folder',
             '/root/import_of_folder/zope2folder'])
        self.assertEqual(importer.getProblems(), [])

        folder = self.root.import_of_folder
        self.assertEqual(folder.get_title(), u"Stuff's container")
        self.assertEqual(folder.objectIds(), ['zope2folder'])
        self.assertEqual(folder.zope2folder.meta_type, 'Folder')

    def test_fallback_existing_replace(self):
        """Import an archive that contain a ZEXP with an object that
        already exists.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Existing folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('zope2folder', 'Existing Zope 2 Stuff')
        factory.manage_addIndexer('indexer', 'Index Zope 2 Stuff')

        importer = self.assertImportZip(
            'test_import_fallback.zip',
            ['/root/folder',
             '/root/folder/zope2folder'],
            replace=True)
        self.assertEqual(importer.getProblems(), [])

        folder = self.root.folder
        self.assertEqual(folder.get_title(), u"Stuff's container")
        self.assertEqual(folder.objectIds(), ['zope2folder'])
        self.assertEqual(folder.zope2folder.meta_type, 'Folder')

    def test_ghost_asset(self):
        """Import a ghost asset pointing to an image.
        """
        importer = self.assertImportZip(
            'test_import_ghost_asset.zip',
            ['/root/folder',
             '/root/folder/torvald',
             '/root/folder/ghost'])
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['torvald',
             'ghost'])

        image = self.root.folder.torvald
        self.assertTrue(interfaces.IImage.providedBy(image))
        self.assertEqual(image.get_web_format(), 'GIF')
        self.assertEqual(image.get_web_scale(), '200%')

        ghost = self.root.folder.ghost
        self.assertTrue(interfaces.IGhostAsset.providedBy(ghost))
        self.assertEqual(ghost.get_haunted(), image)
        self.assertEqual(aq_chain(ghost.get_haunted()), aq_chain(image))

        get_metadata = self.metadata.getMetadata(image).get
        self.assertEqual(
            get_metadata('silva-extra', 'comment'),
            u'Torvald public face.')

    def test_image(self):
        """Import an image.
        """
        importer = self.assertImportZip(
            'test_import_image.zip',
            ['/root/folder',
             '/root/folder/torvald'])
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['torvald'])

        image = self.root.folder.torvald
        self.assertTrue(interfaces.IImage.providedBy(image))
        self.assertEqual(image.get_web_format(), 'GIF')
        self.assertEqual(image.get_web_scale(), '200%')

        get_metadata = self.metadata.getMetadata(image).get
        self.assertEqual(
            get_metadata('silva-extra', 'comment'),
            u'Torvald public face.')

    def test_file(self):
        """Import a file.
        """
        importer = self.assertImportZip(
            'test_import_file.zip',
            ['/root/folder',
             '/root/folder/torvald'])
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['torvald'])

        image = self.root.folder.torvald
        self.assertTrue(interfaces.IFile.providedBy(image))
        self.assertNotEqual(image.get_file_size(), 0)
        self.assertEqual(image.get_filename(), 'torvald.jpeg')

    def test_file_bad_asset(self):
        """Test importing a file with a ZIP where the related file is
        missing.
        """
        importer = self.assertImportZip(
            'test_import_file_bad_asset.zip',
            ['/root/folder',
             '/root/folder/torvald'])
        self.assertEqual(
            importer.getProblems(),
            [('Missing file content.', self.root.folder.torvald)])

        image = self.root.folder.torvald
        self.assertTrue(interfaces.IFile.providedBy(image))
        self.assertEqual(image.get_file_size(), 0)

    def test_ghost_to_link(self):
        """Import a ghost to link.
        """
        importer = self.assertImportZip(
            'test_import_ghost.zip',
            ['/root/folder',
             '/root/folder/public',
             '/root/folder/public/ghost_of_infrae',
             '/root/folder/infrae'])
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['public', 'infrae'])
        self.assertItemsEqual(
            self.root.folder.public.objectIds(),
            ['ghost_of_infrae'])

        link = self.root.folder.infrae
        ghost = self.root.folder.public.ghost_of_infrae
        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IGhost.providedBy(ghost))

        version = ghost.get_viewable()
        self.assertFalse(version is None)
        self.assertEqual(ghost.get_editable(), None)
        self.assertEqual(version.get_title(), u'Public site')
        self.assertEqual(link.get_title(), u'Public site')
        self.assertEqual(version.get_haunted(), link)
        self.assertEqual(aq_chain(version.get_haunted()), aq_chain(link))

        get_metadata = self.metadata.getMetadata(version).get
        self.assertEqual(
            get_metadata('silva-extra', 'comment'),
            u'Public site')

    def test_ghost_to_link_existing_replace(self):
        """Import a ghost to an link to a folder that is already
        existing, replacing it.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        importer = self.assertImportZip(
            'test_import_ghost.zip',
            ['/root/folder',
             '/root/folder/public',
             '/root/folder/public/ghost_of_infrae',
             '/root/folder/infrae'],
            replace=True)
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['public', 'infrae'])
        self.assertItemsEqual(
            self.root.folder.public.objectIds(),
            ['ghost_of_infrae'])

        link = self.root.folder.infrae
        ghost = self.root.folder.public.ghost_of_infrae
        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IGhost.providedBy(ghost))

        version = ghost.get_viewable()
        self.assertFalse(version is None)
        self.assertEqual(ghost.get_editable(), None)
        self.assertEqual(version.get_title(), u'Public site')
        self.assertEqual(version.get_haunted(), link)
        self.assertEqual(aq_chain(version.get_haunted()), aq_chain(link))

    def test_ghost_to_link_existing_rename(self):
        """Import a ghost to a link, in a folder is already existing.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        importer = self.assertImportZip(
            'test_import_ghost.zip',
            ['/root/import_of_folder',
             '/root/import_of_folder/public',
             '/root/import_of_folder/public/ghost_of_infrae',
             '/root/import_of_folder/infrae'])
        self.assertEqual(importer.getProblems(), [])
        # This didn't touch the existing folder
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))
        self.assertItemsEqual(
            self.root.import_of_folder.objectIds(),
            ['public', 'infrae'])
        self.assertItemsEqual(
            self.root.import_of_folder.public.objectIds(),
            ['ghost_of_infrae'])

        link = self.root.import_of_folder.infrae
        ghost = self.root.import_of_folder.public.ghost_of_infrae
        self.assertTrue(interfaces.ILink.providedBy(link))
        self.assertTrue(interfaces.IGhost.providedBy(ghost))

        version = ghost.get_viewable()
        self.assertFalse(version is None)
        self.assertEqual(ghost.get_editable(), None)
        self.assertEqual(version.get_title(), u'Public site')
        self.assertEqual(version.get_haunted(), link)
        self.assertEqual(aq_chain(version.get_haunted()), aq_chain(link))

    def test_ghost_to_folder(self):
        """Test importing a ghost to a folder. It should create a broken ghost.
        """
        importer = self.assertImportFile(
            'test_import_ghost_folder.silvaxml',
            ['/root/folder',
             '/root/folder/container',
             '/root/folder/container/indexer',
             '/root/folder/container/link',
             '/root/folder/ghost'])

        ghost = self.root.folder.ghost
        self.assertTrue(interfaces.IGhost.providedBy(ghost))

        version = ghost.get_viewable()
        self.assertFalse(version is None)
        self.assertEqual(ghost.get_editable(), None)
        self.assertEqual(version.get_title(), u'Ghost target is broken')
        self.assertEqual(version.get_haunted(), None)
        self.assertEqual(
            importer.getProblems(),
            [(u'Ghost target should be a content.', version)])

    def test_ghost_to_folder_loop(self):
        """Test importing a ghost to a parent folder. It should create
        a broken ghost.
        """
        importer = self.assertImportFile(
            'test_import_ghost_loop.silvaxml',
            ['/root/folder',
             '/root/folder/container',
             '/root/folder/container/ghost',
             '/root/folder/container/indexer',
             '/root/folder/container/link'])

        ghost = self.root.folder.container.ghost
        self.assertTrue(interfaces.IGhost.providedBy(ghost))

        version = ghost.get_viewable()
        self.assertFalse(version is None)
        self.assertEqual(ghost.get_editable(), None)
        self.assertEqual(version.get_title(), u'Ghost target is broken')
        self.assertEqual(version.get_haunted(), None)
        self.assertEqual(
            importer.getProblems(),
            [(u'Ghost target creates a circular reference.', version)])

    def test_ghost_to_image(self):
        """Test import a ghost that refer to an image. It is
        impossible and should not be done.
        """
        importer = self.assertImportZip(
            'test_import_ghost_image.zip',
            ['/root/folder',
             '/root/folder/images',
             '/root/folder/images/ghost_of_torvald_jpg',
             '/root/folder/torvald_jpg'])
        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['images', 'torvald_jpg'])
        self.assertItemsEqual(
            self.root.folder.images.objectIds(),
            ['ghost_of_torvald_jpg'])

        image = self.root.folder.torvald_jpg
        ghost = self.root.folder.images.ghost_of_torvald_jpg
        self.assertTrue(interfaces.IImage.providedBy(image))
        self.assertTrue(interfaces.IGhost.providedBy(ghost))

        version = ghost.get_viewable()
        self.assertFalse(version is None)
        self.assertEqual(ghost.get_editable(), None)
        self.assertEqual(version.get_title(), u'Ghost target is broken')
        self.assertEqual(version.get_haunted(), None)
        self.assertEqual(
            importer.getProblems(),
            [(u'Ghost target should be a content.', version)])

    def test_indexer(self):
        """Import an indexer.
        """
        importer = self.assertImportFile(
            'test_import_indexer.silvaxml',
            ['/root/folder',
             '/root/folder/indexer'])
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(self.root.folder.objectIds(), ['indexer'])

        indexer = self.root.folder.indexer
        self.assertTrue(interfaces.IIndexer.providedBy(indexer))
        self.assertEqual(indexer.get_title(), u'Index of this site')

        get_metadata = self.metadata.getMetadata(indexer).get
        self.assertEqual(
            get_metadata('silva-extra', 'comment'),
            u'Nothing special is required.')
        self.assertEqual(
            get_metadata('silva-extra', 'content_description'),
            u'Index the content of your website.')

    def test_ghost_folder(self):
        """Import a ghost folder that contains various things.
        """
        importer = self.assertImportFile(
            'test_import_ghostfolder.silvaxml',
            ['/root/folder',
             '/root/folder/container',
             '/root/folder/container/indexer',
             '/root/folder/container/link',
             '/root/folder/ghost'])
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(
            self.root.folder.objectIds(), ['container', 'ghost'])
        self.assertItemsEqual(
            self.root.folder.container.objectIds(), ['indexer', 'link'])

        folder = self.root.folder.ghost
        container = self.root.folder.container
        self.assertTrue(interfaces.IGhostFolder.providedBy(folder))
        self.assertEqual(container.get_title(), 'Contain some content')
        self.assertEqual(folder.get_title(), 'Contain some content')
        self.assertEqual(folder.get_haunted(), container)
        self.assertEqual(aq_chain(folder.get_haunted()), aq_chain(container))
        self.assertItemsEqual(folder.objectIds(), container.objectIds())

    def test_ghost_folder_existing_rename(self):
        """Import a ghost folder with an ID of a already existing element.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addIndexer('folder', 'Folder')
        self.assertFalse(interfaces.IFolder.providedBy(self.root.folder))

        importer = self.assertImportFile(
            'test_import_ghostfolder.silvaxml',
            ['/root/import_of_folder',
             '/root/import_of_folder/container',
             '/root/import_of_folder/container/indexer',
             '/root/import_of_folder/container/link',
             '/root/import_of_folder/ghost'])
        self.assertEqual(importer.getProblems(), [])
        self.assertFalse(
            interfaces.IFolder.providedBy(self.root.folder))
        self.assertTrue(
            interfaces.IFolder.providedBy(self.root.import_of_folder))
        self.assertItemsEqual(
            self.root.import_of_folder.objectIds(),
            ['container', 'ghost'])
        self.assertItemsEqual(
            self.root.import_of_folder.container.objectIds(),
            ['indexer', 'link'])

        folder = self.root.import_of_folder.ghost
        container = self.root.import_of_folder.container
        self.assertTrue(interfaces.IGhostFolder.providedBy(folder))
        self.assertEqual(folder.get_haunted(), container)
        self.assertEqual(aq_chain(folder.get_haunted()), aq_chain(container))
        self.assertItemsEqual(folder.objectIds(), container.objectIds())

    def test_ghost_folder_to_link(self):
        """Test creating a ghost folder that points to a link. This
        should create a broken ghost folder.
        """
        importer = self.assertImportFile(
            'test_import_ghostfolder_link.silvaxml',
            ['/root/folder',
             '/root/folder/container',
             '/root/folder/container/indexer',
             '/root/folder/container/link',
             '/root/folder/ghost'])
        self.assertItemsEqual(
            self.root.folder.objectIds(), ['container', 'ghost'])
        self.assertItemsEqual(
            self.root.folder.container.objectIds(), ['indexer', 'link'])

        folder = self.root.folder.ghost
        self.assertTrue(interfaces.IGhostFolder.providedBy(folder))
        self.assertEqual(folder.get_haunted(), None)
        self.assertEqual(folder.get_title(), 'Ghost target is broken')
        self.assertItemsEqual(folder.objectIds(), [])
        self.assertEqual(
            importer.getProblems(),
            [(u'Ghost target should be a container.', folder)])

    def test_ghost_folder_loop(self):
        """Test creating a ghost folder that points to one of its
        parents. This should create a broken ghost folder.
        """
        importer = self.assertImportFile(
            'test_import_ghostfolder_loop.silvaxml',
            ['/root/folder',
             '/root/folder/container',
             '/root/folder/container/indexer',
             '/root/folder/container/link',
             '/root/folder/container/ghost'])

        self.assertItemsEqual(
            self.root.folder.objectIds(),
            ['container'])
        self.assertItemsEqual(
            self.root.folder.container.objectIds(),
            ['ghost', 'indexer', 'link'])

        folder = self.root.folder.container.ghost
        self.assertTrue(interfaces.IGhostFolder.providedBy(folder))
        self.assertEqual(folder.get_haunted(), None)
        self.assertEqual(folder.get_title(), 'Ghost target is broken')
        self.assertItemsEqual(folder.objectIds(), [])
        self.assertEqual(
            importer.getProblems(),
            [(u'Ghost target creates a circular reference.', folder)])

    def test_autotoc(self):
        """Import an AutoTOC.
        """
        importer = self.assertImportFile(
            'test_import_autotoc.silvaxml',
            ['/root/folder',
             '/root/folder/assets',
             '/root/folder/index'])
        self.assertEqual(importer.getProblems(), [])
        self.assertItemsEqual(self.root.folder.objectIds(), ['assets', 'index'])

        assets = self.root.folder.assets
        containers = self.root.folder.index
        self.assertTrue(interfaces.IAutoTOC.providedBy(assets))
        self.assertTrue(interfaces.IAutoTOC.providedBy(containers))
        self.assertEqual(assets.get_title(), u'Local assets')
        self.assertEqual(containers.get_title(), u'Containers')

        self.assertEqual(assets.get_show_icon(), True)
        self.assertEqual(containers.get_show_icon(), False)
        self.assertEqual(assets.get_toc_depth(), -1)
        self.assertEqual(containers.get_toc_depth(), 42)
        self.assertItemsEqual(
            assets.get_local_types(),
            [u'Silva File', u'Silva Image'])
        self.assertItemsEqual(
            containers.get_local_types(),
            [u'Silva Folder', u'Silva Publication'])

        get_metadata = self.metadata.getMetadata(assets).get
        self.assertEqual(
            get_metadata('silva-settings', 'hide_from_tocs'),
            u'hide')
        self.assertEqual(
            get_metadata('silva-extra', 'content_description'),
            u'Report local assets.')

    def test_problems(self):
        """Import a Silva content that few problems advertised in the
        XML.
        """
        importer = self.assertImportFile(
            'test_import_problems.silvaxml',
            ['/root/folder',
             '/root/folder/link',
             '/root/folder/index'])

        folder = self.root.folder
        version = folder.link.get_viewable()
        self.assertEqual(
            importer.getProblems(),
            [(u'Spaceship life support is failing.', version),
             (u'Spaceship is out of fuel.', folder)])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLImportTestCase))
    return suite

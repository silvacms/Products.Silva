import os
import xml.sax
from xml.sax.handler import feature_namespaces

import SilvaTestCase
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva import mangle
from Products.Silva.silvaxml import xmlimport 
from Products.Silva.interfaces import IGhost, IContainer
from DateTime import DateTime

def testopen(path, rw):
    directory = os.path.dirname(__file__)
    return open(os.path.join(directory, path), rw)

class SetTestCase(SilvaTestCase.SilvaTestCase):
    
    def test_publication_import(self):
        source_file = testopen('data/test_publication.xml', 'r')
        xmlimport.importFromFile(
            source_file, self.root)
        source_file.close()
        publication = self.root.testpublication
        self.assertEquals(
            u'Publication',
            publication.get_title())
            
    def test_folder_import(self):
        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        source_file = testopen('data/test_folder.xml', 'r')
        xmlimport.importFromFile(
            source_file, importfolder)
        source_file.close()
        folder = importfolder.testfolder.testfolder2
        self.assertEquals(
            u'This is &another; testfolder',
            folder.get_title())
        
    def test_link_import(self):
        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        source_file = testopen('data/test_link.xml', 'r')
        xmlimport.importFromFile(
            source_file, importfolder)
        source_file.close()
        linkversion = importfolder.testfolder.testfolder2.test_link.get_editable()
        linkversion2 = importfolder.testfolder.testfolder2.test_link.get_previewable()
        self.assertEquals(
            'approved title',
            linkversion.get_title())
        self.assertEquals(
            'approved title',
            linkversion.get_title())
        self.assertEquals(
            DateTime('2004-04-23T16:13:40Z'),
            linkversion.get_modification_datetime())
        metadata_service = linkversion.service_metadata
        binding = metadata_service.getMetadata(linkversion)
        self.assertEquals(
           'test_user_1_',
            binding._getData(
                'silva-extra').data['creator'])

    def test_autotoc_import(self):
        source_file = testopen('data/test_autotoc.xml', 'r')
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

    def test_ghost_import(self):
        # import the ghost
        source_file = testopen('data/test_link.xml', 'r')
        xmlimport.importFromFile(
            source_file,
            self.root)
        source_file.close()

        source_file = testopen('data/test_ghost.xml', 'r')
        xmlimport.importFromFile(
            source_file,
            self.root)
        source_file.close()
        version = self.root.testfolder3.caspar.get_editable()
        version2 = self.root.testfolder3.caspar.get_previewable()
        self.assertEquals(version.id, version2.id)
        self.assertEquals(
            'test_link',
            version.get_title()
            )
        self.assertEquals(
            'Silva Ghost Version',
            version.meta_type
            )

    def test_ghostfolder_import(self):
        importfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        haunted_folder = self.add_folder(
            importfolder,
            'testfolder2',
            'This is <boo>a</boo> haunted testfolder',
            policy_name='Silva AutoTOC')
        # add some content.
        haunted_folder.manage_addProduct['SilvaDocument'].manage_addDocument(
            'foo', 'Foo')

        
        metadata_service = haunted_folder.service_metadata
        binding = metadata_service.getMetadata(haunted_folder)
        binding._setData({'creator': 'ghost dog'}, 'silva-extra')
        # import the ghost folder
        source_file = testopen('data/test_ghost_folder.xml', 'r')
        xmlimport.importFromFile(
            source_file,
            self.root)
        source_file.close()
        version = self.root.testfolder3.caspar.get_editable()
        version2 = self.root.testfolder3.caspar.get_previewable()

        self.assertEquals(version.id, version2.id)
        self.assertEquals(
            'This is <boo>a</boo> haunted testfolder',
            version.get_title()
            )
        self.assertEquals(
            '/root/testfolder/testfolder2',
            version.get_haunted_url()
            )
        self.assertEquals(
            'Silva Ghost Folder',
            version.meta_type
            )

        # test if sync has been done
        haunted_ids = list(haunted_folder.objectIds())
        ghost_ids = list(version.objectIds())
        self.assertEquals(haunted_ids.sort(), ghost_ids.sort())
        metadata_service = version.service_metadata
        binding = metadata_service.getMetadata(version)
        self.assertEquals(
           'ghost dog',
            binding._getData(
                'silva-extra').data['creator'])
        # check whether we got ghosts (or subcontainers)
        for obj in version.objectValues():            
            self.assert_(
                IGhost.providedBy(obj) or
                IContainer.providedBy(obj))

    def test_indexer_import(self):
        source_file = testopen('data/test_indexer.xml', 'r')
        xmlimport.importFromFile(
            source_file,
            self.root)
        source_file.close()
        indexer = self.root.testfolder.Indexer
        self.assertEquals('Index', indexer.get_title())
        self.assertEquals('Silva Indexer', indexer.meta_type)

    def test_metadata_import(self):
	# this is a reproduction of the xmlimport bug
	# which causes import to fail if an installed metadata set is not
	# present in the import
	importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        source_file = testopen('data/test_metadata_import.xml', 'r')
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

    def test_zip_import(self):
        from StringIO import StringIO
        from zipfile import ZipFile
        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        directory = os.path.dirname(__file__)
        zip_file = ZipFile(
            os.path.join(directory, 'data/test_export.zip'), 'r')
        test_info = xmlimport.ImportInfo()
        test_info.setZipFile(zip_file)
        bytes = zip_file.read('silva.xml')
        source_file = StringIO(bytes)
        xmlimport.importFromFile(
            source_file,
            importfolder,
            info=test_info)
        source_file.close()
        zip_file.close()
        # normal xml import works
        self.assertEquals(
            'test_link',
            importfolder.testfolder.testfolder2.test_link.id)
        # asset file import works
        self.assertEquals(
            'sound1.wav',
            importfolder.testfolder.testfolder2['testzip']['sound1.wav'].id)
        self.assertEquals(
            'Silva File',
            importfolder.testfolder.testfolder2['testzip']['sound1.wav'].meta_type)
        # image file import works:
        self.assertEquals(
            'image5.jpg',
            importfolder.testfolder.testfolder2.testzip.foo.bar.baz['image5.jpg'].id)
        self.assertEquals(
            'Silva Image',
            importfolder.testfolder.testfolder2.testzip.foo.bar.baz['image5.jpg'].meta_type) 
        # ghost import
        self.assertEquals(
            'Silva Ghost',
            importfolder.testfolder.testfolder2['haunting_the_neighbour'].meta_type) 
        self.assertEquals(
            '/silva/silva/testfolder/testfolder2/test_link',
            importfolder.testfolder.testfolder2['haunting_the_neighbour'].get_haunted_url()) 

    def test_replace_objects(self):
        source_file = testopen('data/test_autotoc.xml', 'r')
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

        source_file = testopen('data/test_autotoc2.xml', 'r')
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

        
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SetTestCase))
    return suite    

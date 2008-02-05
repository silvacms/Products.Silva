# Copyright (c) 2003-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.6 $
import SilvaTestCase

from Products.Silva.adapters import archivefileimport
from AccessControl.SecurityManagement import newSecurityManager

from Products.Silva import Image, File

# Constructing some testable zipfile
import os
from os.path import join
directory = os.path.dirname(__file__)
zipfile1 = open(join(directory,'data','test1.zip'))
zipfile2 = open(join(directory,'data','test2.zip'))


"""
Test file 'test1.zip' structure:

  testzip
  |-- Clock.swf
  |-- bar
  |   `-- image2.jpg
  |-- foo
  |   |-- bar
  |   |   |-- baz
  |   |   |   `-- image5.jpg
  |   |   `-- image4.jpg
  |   `-- image3.jpg
  |-- image1.jpg
  `-- sound1.mp3

Test file 'test2.zip' structure:

  Clock.swf
  image1.jpg
  sound1.mp3
"""

class ArchiveFileImportTestCase(SilvaTestCase.SilvaTestCase):
    def test_getAdapter(self):
        folder = self.add_folder(self.root, 'foo', 'FooFolder')
        adapter = archivefileimport.getArchiveFileImportAdapter(folder)
        self.assert_(
            isinstance(adapter, archivefileimport.ArchiveFileImportAdapter))
        document = self.add_document(self.root, 'bar', 'BarDocument')
        adapter = archivefileimport.getArchiveFileImportAdapter(document)        
        self.assertEquals(None, adapter)
    
    def test_importArchiveFileDefaultSettings(self):
        folder = self.add_folder(self.root, 'foo', 'FooFolder')
        adapter = archivefileimport.getArchiveFileImportAdapter(folder)
        succeeded, failed = adapter.importArchive(zipfile1)
        succeslist = [
            'testzip/foo/bar/baz/image5.jpg', 
            'testzip/foo/bar/image4.jpg', 
            'testzip/foo/image3.jpg', 
            'testzip/bar/image2.jpg', 
            'testzip/image1.jpg', 
            'testzip/sound1.mp3', 
            'testzip/Clock.swf']
        self.assertEquals(succeslist, succeeded)
        self.assertEquals([], failed)
        self.assert_(folder['testzip'])
        self.assert_(folder['testzip']['bar'])
        self.assert_(folder['testzip']['foo'])
        self.assert_(folder['testzip']['foo']['bar'])
        self.assert_(folder['testzip']['foo']['bar']['baz'])
        object = folder['testzip']['image1.jpg']
        self.assert_(isinstance(object, Image.Image))
        object = folder['testzip']['sound1.mp3']
        self.assert_(isinstance(object, File.File))
        object = folder['testzip']['bar']['image2.jpg']
        self.assert_(isinstance(object, Image.Image))
        object = folder['testzip']['foo']['bar']['baz']['image5.jpg']
        self.assert_(isinstance(object, Image.Image))
        # I'd like to test the flash asset, but it is not in Silva core.
        object = folder['testzip']['Clock.swf']
        self.assert_(isinstance(object, File.File))
    
    def test_importArchiveFileDefaultSettingsNoSubdirsInArchive(self):
        folder = self.add_folder(self.root, 'foo', 'FooFolder')
        adapter = archivefileimport.getArchiveFileImportAdapter(folder)
        succeeded, failed = adapter.importArchive(zipfile2)
        succeslist = ['Clock.swf', 'image1.jpg', 'sound1.mp3']
        self.assertEquals(succeslist, succeeded)
        self.assertEquals([], failed)
        object = folder['image1.jpg']
        self.assert_(isinstance(object, Image.Image))
        object = folder['sound1.mp3']
        self.assert_(isinstance(object, File.File))
        # I'd like to test the flash asset, but it is not in Silva core.
        object = folder['Clock.swf']
        self.assert_(isinstance(object, File.File))
        
    def test_importArchiveFileTitleSet(self):
        folder = self.add_folder(self.root, 'foo', 'FooFolder')
        adapter = archivefileimport.getArchiveFileImportAdapter(folder)
        succeeded, failed = adapter.importArchive(
            zipfile1, assettitle=u'Daarhelemali\x00EB')
        object = folder['testzip']['bar']['image2.jpg']
        self.assertEquals(u'Daarhelemali\x00EB', object.get_title())
        object = folder['testzip']['foo']['bar']['baz']['image5.jpg']
        self.assertEquals(u'Daarhelemali\x00EB', object.get_title())
    
    def test_importArchiveFileNoRecreateDirs(self):
        folder = self.add_folder(self.root, 'foo', 'FooFolder')
        adapter = archivefileimport.getArchiveFileImportAdapter(folder)
        succeeded, failed = adapter.importArchive(zipfile1, recreatedirs=0)
        self.assert_(folder['testzip_foo_bar_baz_image5.jpg'])
        self.assert_(folder['testzip_foo_bar_image4.jpg'])
        self.assert_(folder['testzip_foo_image3.jpg'])
        self.assert_(folder['testzip_bar_image2.jpg'])
        self.assert_(folder['testzip_image1.jpg'])
        self.assert_(folder['testzip_sound1.mp3'])
        self.assert_(folder['testzip_Clock.swf'])
        self.assert_(isinstance(folder['testzip_image1.jpg'], Image.Image))
        self.assert_(isinstance(folder['testzip_sound1.mp3'], File.File))
        self.assert_(isinstance(folder['testzip_Clock.swf'], File.File))

    def test_importArchiveFileNoRecreateDirsNoSubdirsInArchive(self):
        folder = self.add_folder(self.root, 'foo', 'FooFolder')
        adapter = archivefileimport.getArchiveFileImportAdapter(folder)
        succeeded, failed = adapter.importArchive(zipfile2, recreatedirs=0)
        self.assert_(folder['image1.jpg'])
        self.assert_(folder['sound1.mp3'])
        self.assert_(folder['Clock.swf'])
        self.assert_(isinstance(folder['image1.jpg'], Image.Image))
        self.assert_(isinstance(folder['sound1.mp3'], File.File))
        self.assert_(isinstance(folder['Clock.swf'], File.File))
        
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ArchiveFileImportTestCase))
    return suite

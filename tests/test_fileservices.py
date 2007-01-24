# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_fileservices.py,v 1.6 2006/01/24 16:13:33 faassen Exp $
import os
import SilvaTestCase
from Testing.ZopeTestCase.ZopeTestCase import ZopeTestCase
from Testing.ZopeTestCase import utils

from StringIO import StringIO

from Products.Silva import File

try:
    from Products import ExtFile
    WITH_EXTFILE = True
except ImportError, e:
    WITH_EXTFILE = False
    
# NOTE: these tests should all pass regardless of the availability of ExtFile

def testopen(path, rw):
    directory = os.path.dirname(__file__)
    return open(os.path.join(directory, path), rw)

class FileServicesTest(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        """
        Test content structure:
        
        root/service_files (by default)
        root/folder1
        root/folder1/folder1in1
        root/folder1/folder1in1/folder1in1in1
        root/folder1/folder1in1/folder1in1in1/service_files
        root/folder2
        """
        root = self.root = self.getRoot()
        folder1 = self.add_folder(root, 'folder1', 'Folder 1')
        folder2 = self.add_folder(root, 'folder2', 'Folder 2')
        folder1in1 = self.add_folder(folder1, 'folder1in1', 'Folder 1 in 1')
        folder1in1in1 = self.add_folder(folder1in1, 'folder1in1in1', 'Folder 1 in 1 in 1')
        folder1in1.manage_addProduct['Silva'].manage_addFilesService(
            'service_files', 'Other Files Service')
    
    def _app(self):
        app = ZopeTestCase._app(self)
        app = app.aq_base
        request_out = self.request_out = StringIO()
        return utils.makerequest(app, request_out)

    def _test_file(self, id, context):
        file_handle = testopen('test_image_data/photo.tif', 'rb')
        context.manage_addProduct['Silva'].manage_addFile(
            id, 'Test File', file_handle)
        file_handle.close()

    def _test_image(self, id, context):
        file_handle = testopen('test_image_data/photo.tif', 'rb')
        context.manage_addProduct['Silva'].manage_addImage(
            id, 'Test Image', file_handle)
        file_handle.close()
            
    def _get_req_data(self, data):
        if data:
            s = data
        else:
            s = self.request_out.getvalue()
            self.request_out.seek(0)
            self.request_out.truncate()
        if s.startswith('Status: 200'):
            s = s[s.find('\n\n')+2:]
        return s
    
    def test_file_extfile(self):
        self.root.service_files.manage_filesServiceEdit('', 1, '')
        self.assertEqual(
            self.root.service_files.useFSStorage(), WITH_EXTFILE)
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.useFSStorage(), False)
        self._test_file('testfile', self.root)
        self._test_file('testfile', self.root.folder2)
        self.root.folder1.folder1in1.service_files.manage_filesServiceEdit('', 1, '')
        self.assertEqual(
            self.root.service_files.useFSStorage(), WITH_EXTFILE)
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.useFSStorage(), WITH_EXTFILE)
        self._test_file('testfile', self.root.folder1.folder1in1)
        self._test_file('testfile', self.root.folder1.folder1in1.folder1in1in1)        
    
    def test_file_zodb_implicitly(self):
        # By default fs storage is not enabled, so test that
        self.assertEqual(self.root.service_files.useFSStorage(), False)
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.useFSStorage(), False)
        self._test_file('testfile', self.root)
        self._test_file('testfile', self.root.folder2)
        self.assertEqual(self.root.service_files.useFSStorage(), False)
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.useFSStorage(), False)
        self._test_file('testfile', self.root.folder1.folder1in1)
        self._test_file('testfile', self.root.folder1.folder1in1.folder1in1in1)        

    def test_file_zodb_explicitly(self):
        # Explicitly disable fs storage
        self.root.service_files.manage_filesServiceEdit('', 0, '')
        self.assertEqual(self.root.service_files.useFSStorage(), False)
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.useFSStorage(), False)
        self._test_file('testfile', self.root)
        self._test_file('testfile', self.root.folder2)
        self.root.folder1.folder1in1.service_files.manage_filesServiceEdit('', 0, '')
        self.assertEqual(self.root.service_files.useFSStorage(), False)
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.useFSStorage(), False)
        self._test_file('testfile', self.root.folder1.folder1in1)
        self._test_file('testfile', self.root.folder1.folder1in1.folder1in1in1)        
        
    def test_is_filesystem_storage_available(self):
        self.assertEqual(
            self.root.service_files.is_filesystem_storage_available(), 
            WITH_EXTFILE)
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.is_filesystem_storage_available(), 
            WITH_EXTFILE)

    def test_filesystem_storage_enabled(self):
        # By default fs storage is not enabled, so test that
        self.assertEqual(
            self.root.service_files.filesystem_storage_enabled(), False)
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.filesystem_storage_enabled(),
            False)
        # Then enable it
        self.root.service_files.manage_filesServiceEdit('', 1, '')
        self.assertEqual(
            self.root.service_files.filesystem_storage_enabled(), True)
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.filesystem_storage_enabled(),
            False)
        self.root.folder1.folder1in1.service_files.manage_filesServiceEdit('', 1, '')
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.filesystem_storage_enabled(),
            True)
        # Explicitly disable fs storage
        self.root.service_files.manage_filesServiceEdit('', 0, '')
        self.assertEqual(
            self.root.service_files.filesystem_storage_enabled(), False)
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.filesystem_storage_enabled(),
            True)
        self.root.folder1.folder1in1.service_files.manage_filesServiceEdit('', 0, '')
        self.assertEqual(
            self.root.folder1.folder1in1.service_files.filesystem_storage_enabled(),
            False)

    # Covered by the test_file_zodb and test_file_extfile tests I guess
    #def test_useFSStorage(self):
    #    pass
    
    def test_filesystem_path(self):
        # XXX this needs an actual test!        
        #print self.root.service_files.filesystem_path()
        #print self.root.service_files.folder1.folder1in1.filesystem_path()
        pass
    
    # Covered by the test_filesystem_path, test_file_zodb and
    # test_file_extfile tests I guess
    #def test_manage_filesServiceEdit(self):
    #    pass
    
    def test_manage_convertStorage(self):
        # by default we use ZODB storage
        self._test_image('testimage', self.root)
        self._test_image('testimage', self.root.folder1)
        self._test_image('testimage', self.root.folder1.folder1in1)       
        self._test_image('testimage', self.root.folder2)
        self._test_file('testfile', self.root)
        self._test_file('testfile', self.root.folder1.folder1in1)
        self.assertEqual(self.root.testimage.image.meta_type, 'Image')
        self.assertEqual(
            self.root.folder1.testimage.image.meta_type, 'Image')
        self.assertEqual(
            self.root.folder1.folder1in1.testimage.image.meta_type, 'Image')
        self.assertEqual(
            self.root.folder2.testimage.image.meta_type, 'Image')
        self.assertEqual(
            self.root.folder2.testimage.image.meta_type, 'Image')
        self.assertEqual(
            self.root.testfile._file.meta_type, 'File')
        self.assertEqual(
            self.root.folder1.folder1in1.testfile._file.meta_type, 'File')
        if WITH_EXTFILE:
            self.root.service_files.manage_filesServiceEdit('', 1, '')
            self.root.service_files.manage_convertStorage()
            self.assertEqual(self.root.testimage.image.meta_type, 'ExtImage')
            self.assertEqual(
                self.root.folder1.testimage.image.meta_type, 'ExtImage')
            self.assertEqual(
                self.root.folder1.folder1in1.testimage.image.meta_type, 'Image')
            self.assertEqual(
                self.root.folder2.testimage.image.meta_type, 'ExtImage')
            self.assertEqual(
                self.root.testfile._file.meta_type, 'ExtFile')
            self.assertEqual(
                self.root.folder1.folder1in1.testfile._file.meta_type, 'File')
            self.root.folder1.folder1in1.service_files.manage_filesServiceEdit('', 1, '')
            self.root.folder1.folder1in1.service_files.manage_convertStorage()
            self.assertEqual(self.root.testimage.image.meta_type, 'ExtImage')
            self.assertEqual(
                self.root.folder1.testimage.image.meta_type, 'ExtImage')
            self.assertEqual(
                self.root.folder1.folder1in1.testimage.image.meta_type, 'ExtImage')
            self.assertEqual(
                self.root.folder2.testimage.image.meta_type, 'ExtImage')
            self.assertEqual(
                self.root.testfile._file.meta_type, 'ExtFile')
            self.assertEqual(
                self.root.folder1.folder1in1.testfile._file.meta_type, 'ExtFile')
            self.root.service_files.manage_filesServiceEdit('', 0, '')
            self.root.service_files.manage_convertStorage()
            self.assertEqual(self.root.testimage.image.meta_type, 'Image')
            self.assertEqual(
                self.root.folder1.testimage.image.meta_type, 'Image')
            self.assertEqual(
                self.root.folder1.folder1in1.testimage.image.meta_type, 'ExtImage')
            self.assertEqual(
                self.root.folder2.testimage.image.meta_type, 'Image')
            self.assertEqual(
                self.root.testfile._file.meta_type, 'File')
            self.assertEqual(
                self.root.folder1.folder1in1.testfile._file.meta_type, 'ExtFile')
        
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileServicesTest))
    return suite

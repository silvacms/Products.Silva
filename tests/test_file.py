# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import component
from zope.interface.verify import verifyObject

import SilvaTestCase
import helpers

from silva.core import interfaces
from Products.Silva import File

class FileTest(SilvaTestCase.SilvaFileTestCase):

    def _test_file(self):
        file_handle = helpers.openTestFile('photo.tif')
        file_data = file_handle.read()
        file_size = file_handle.tell()
        file_handle.seek(0)
        self.root.manage_addProduct['Silva'].manage_addFile('testfile',
            'Test File', file_handle)
        file_handle.close()
        file = self.root.testfile
        self.failUnless(verifyObject(interfaces.IAsset, file))
        self.failUnless(verifyObject(interfaces.IFile, file))
        self.assertEqual(file_size, file.get_file_size())
        self.failUnless(file.get_download_url() is not None)
        self.failUnless(file.tag() is not None)

        data = component.queryMultiAdapter((file, file.REQUEST), name='index')()
        self.assertEqual(file_data, self.get_request_data(data))

        assetdata = interfaces.IAssetData(file)
        self.failUnless(verifyObject(interfaces.IAssetData, assetdata))
        self.assertEquals(file_data, assetdata.getData())


    def test_file_blob(self):
        self.root.service_files.storage = File.BlobFile
        self._test_file()

    def test_file_zodb_default(self):
        if self.root.service_files.storage is None:
            self._test_file()

    def test_file_zodb(self):
        self.root.service_files.storage = File.ZODBFile
        self._test_file()

    def test_file_extfile(self):
        if File.FILESYSTEM_STORAGE_AVAILABLE:
            self.root.service_files.storage = File.FileSystemFile
            self._test_file()


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileTest))
    return suite

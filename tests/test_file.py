# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_file.py,v 1.7 2006/01/24 16:13:33 faassen Exp $
import os
import SilvaTestCase
from Testing.ZopeTestCase.ZopeTestCase import ZopeTestCase
from Testing.ZopeTestCase import utils

from StringIO import StringIO

from Products.Silva import File


class FileTest(SilvaTestCase.SilvaTestCase):
    """Test file implementation.
    """

    def _app(self):
        app = ZopeTestCase._app(self)
        self.request_out = StringIO()
        return utils.makerequest(app.aq_base, self.request_out)

    def test_cookpath(self):
        self.assertEqual(File.cookPath("foo/bar/baz"), ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("/foo/bar/baz"), ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("foo/../bar/baz"),
            ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("foo/bar//baz"),
            ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("foo/bar/./baz"),
            ('foo', 'bar', 'baz'))

    def _test_file(self):
        directory = os.path.dirname(__file__)
        file_handle = open(os.path.join(directory,
                                        'test_image_data/photo.tif'), 'rb')
        file_data = file_handle.read()
        file_handle.seek(0)
        self.root.manage_addProduct['Silva'].manage_addFile('testfile',
            'Test File', file_handle)
        file_handle.close()
        data = self.root.testfile.index_html()
        silva_data = self._get_req_data()
        self.assertEqual(
            file_data, silva_data, "Asset didn't return original data")

    def test_file_extfile(self):
        self.root.service_files.manage_filesServiceEdit('', 1)
        self._test_file()

    def test_file_zodb(self):
        self.root.service_files.manage_filesServiceEdit('', 0)
        self._test_file()

    def _get_req_data(self):
        content = self.request_out.getvalue()
        self.request_out.seek(0)
        self.request_out.truncate()
        if content.startswith('Status: 200'):
            return content[content.find('\r\n\r\n')+4:]
        return content

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileTest))
    return suite

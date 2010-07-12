# Copyright (c) 2005-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import SilvaTestCase
import unittest

from Products.Silva.testing import FunctionalLayer
from silva.core.interfaces.adapters import IPath


class PathAdapterTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        # add a folder that can function as the virtual host root
        self.root.manage_addProduct['Silva'].manage_addFolder(
            'folder', 'Folder')
        self.folder = self.root.folder
        self.document = self.root.folder.index

        request = self.request = self.root.REQUEST
        request.environ['HTTP_HOST'] = 'example.com:80'
        request['PARENTS'] = [self.root.folder]
        request.setServerURL(
            protocol='http', hostname='example.com', port='80')
        request.setVirtualRoot(('', ))

    def test_request_pathToUrlPath(self):
        path_adapter = IPath(self.request)
        ptu = path_adapter.pathToUrlPath
        self.assertEquals(
            ptu('folder'),
            'folder')
        self.assertEquals(
            ptu('index'),
            'index')
        self.assertEquals(
            ptu('index#anchor'),
            'index#anchor')
        self.assertEquals(
            ptu('/root/folder/index'),
            '/index')
        self.assertEquals(
            ptu('/root/folder/index#anchor'),
            '/index#anchor')

        # If you give a valid URL it should not be touched
        self.assertEquals(
            ptu('http://somewhere.com:80/index#anchor'),
            'http://somewhere.com:80/index#anchor')
        self.assertEquals(
            ptu('http://example.com:80/index#anchor'),
            'http://example.com:80/index#anchor')
        self.assertEquals(
            ptu('tel:+31 10 2140440'),
            'tel:+31 10 2140440')

    def test_request_urlToPath(self):
        path_adapter = IPath(self.request)
        utp = path_adapter.urlToPath
        self.assertEquals(
            utp('index'),
            'index')
        self.assertEquals(
            utp('folder/index'),
            'folder/index')
        self.assertEquals(
            utp('folder/index#anchor'),
            'folder/index#anchor')
        self.assertEquals(
            utp('/index'),
            '/root/folder/index')
        self.assertEquals(
            utp('/index?p=b'),
            '/root/folder/index?p=b')
        self.assertEquals(
            utp('/index#anchor'),
            '/root/folder/index#anchor')
        self.assertEquals(
            utp('/index?p=b#anchor'),
            '/root/folder/index?p=b#anchor')
        self.assertEquals(
            utp('http://example.com:80/index'),
            '/root/folder/index')
        self.assertEquals(
            utp('http://example.com:80/index#anchor'),
            '/root/folder/index#anchor')
        self.assertEquals(
            utp('tel:+31 10 2140440'),
            'tel:+31 10 2140440')

    def test_silva_pathToUrlPath(self):
        # test the ISilvaObject SilvaPathAdapter, which converts
        # the url attribute of silvaxml <link> tags to href= values.
        # in some circumstances, the IHTTPRequest IPath adapter will
        # be used to finalize the url of an absolute or relative path
        path_adapter = IPath(self.document)
        ptup = path_adapter.pathToUrlPath

        self.assertEquals(
            ptup("mailto:f.o'last@someplace.com"),
            "mailto:f.o'last@someplace.com")
        self.assertEquals(
            ptup('tel:+31 10 2140440'),
            'tel:+31 10 2140440')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PathAdapterTestCase))
    return suite

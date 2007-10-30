# Copyright (c) 2005-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $
import SilvaTestCase

from Products.Silva.adapters import path

class PathAdapterTestCase(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        # add a folder that can function as the virtual host root
        self.root.manage_addProduct['Silva'].manage_addFolder('foo', 'Foo')
        self.foo = self.root.foo
        self.document = self.root.foo.index
                                                            
        request = self.request = self.app.REQUEST
        request['PARENTS'] = [self.root.foo]
        request.setServerURL(
            protocol='http', hostname='foo.bar.com', port='80')
        request.setVirtualRoot(('', ))
    
    def test_pathToUrlPath(self):
        path_adapter = path.getPathAdapter(self.request)
        ptu = path_adapter.pathToUrlPath
        self.assertEquals(ptu('foo'), 'foo')
        self.assertEquals(ptu('index'), 'index')
        self.assertEquals(ptu('index#anchor'), 'index#anchor')
        self.assertEquals(ptu('/root/foo/index'), '/index')
        self.assertEquals(ptu('/root/foo/index#anchor'), '/index#anchor')

    def test_urlToPath(self):
        path_adapter = path.getPathAdapter(self.request)
        utp = path_adapter.urlToPath
        self.assertEquals(utp('index'), 'index')
        self.assertEquals(utp('foo/index'), 'foo/index')
        self.assertEquals(utp('foo/index#anchor'), 'foo/index#anchor')
        self.assertEquals(utp('/index'), '/root/foo/index')
        self.assertEquals(utp('http://foo.bar.com:80/index'), 
                                '/root/foo/index')
        self.assertEquals(utp('http://foo.bar.com:80/index#anchor'), 
                                '/root/foo/index#anchor')
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PathAdapterTestCase))
    return suite

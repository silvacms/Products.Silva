# Copyright (c) 2005-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision$
import SilvaTestCase

from silva.core.interfaces.adapters import IPath

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
        path_adapter = IPath(self.request)
        ptu = path_adapter.pathToUrlPath
        self.assertEquals(ptu('foo'), 'foo')
        self.assertEquals(ptu('index'), 'index')
        self.assertEquals(ptu('index#anchor'), 'index#anchor')
        self.assertEquals(ptu('/root/foo/index'), '/index')
        self.assertEquals(ptu('/root/foo/index#anchor'), '/index#anchor')

    def test_urlToPath(self):
        path_adapter = IPath(self.request)
        utp = path_adapter.urlToPath
        self.assertEquals(utp('index'), 'index')
        self.assertEquals(utp('foo/index'), 'foo/index')
        self.assertEquals(utp('foo/index#anchor'), 'foo/index#anchor')
        self.assertEquals(utp('/index'), '/root/foo/index')
        self.assertEquals(utp('/index?p=b'), '/root/foo/index?p=b')
        self.assertEquals(utp('/index#anchor'), '/root/foo/index#anchor')
        self.assertEquals(utp('/index?p=b#anchor'), '/root/foo/index?p=b#anchor')
        self.assertEquals(utp('http://foo.bar.com:80/index'), 
                                '/root/foo/index')
        self.assertEquals(utp('http://foo.bar.com:80/index#anchor'), 
                                '/root/foo/index#anchor')
        
    def test_ISilvaObject_pathToUrlPath(self):
        #test the ISilvaObject SilvaPathAdapter, which converts
        # the url attribute of silvaxml <link> tags to href= values.
        # in some circumstances, the IHTTPRequest IPath adapter will
        # be used to finalize the url of an absolute or relative path
        path_ad = IPath(self.document)
        ptup = path_ad.pathToUrlPath
        #make sure mailto links with uncommon characters in the
        #mailbox work
        self.assertEquals(ptup("mailto:f.o'last@someplace.com"),
                          "mailto:f.o'last@someplace.com")
        
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PathAdapterTestCase))
    return suite

# Copyright (c) 2003-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Silva
from Products.Silva import assetregistry
from Products.SilvaDocument import Document

import SilvaTestCase

class AssetRegistryTestCase(SilvaTestCase.SilvaTestCase):
    # NOTE:
    #
    # I'm using SilvaDocument as a 'test' extension for testing
    # this registry since SilvaDocument is supposed to be always available.
    #
    def test_registerFactoryForMimetype(self):
        factory = Document.manage_addDocument
        mimetype = 'application/x-test-mimetype-1'
        assetregistry.registerFactoryForMimetype(mimetype, factory, 'Silva')
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetype))
        mimetype = 'application/x-test-mimetype-2'
        assetregistry.registerFactoryForMimetype(
            mimetype, factory, 'SilvaDocument')
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetype))

    def test_registerFactoryForMultipleMimetypes(self):
        factory = Document.manage_addDocument
        mimetypes = (
            'application/x-test-mimetype-1', 'application/x-test-mimetype-2',
            'application/x-test-mimetype-3', 'application/x-test-mimetype-4')
        assetregistry.registerFactoryForMimetypes(
            mimetypes, factory, 'Silva')
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetypes[0]))
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetypes[1]))
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetypes[2]))
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetypes[3]))
            
    def test_unregisterFactory(self):
        factory = Document.manage_addDocument
        mimetype = 'application/x-test-mimetype-1'
        assetregistry.registerFactoryForMimetype(mimetype, factory, 'Silva')
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetype))
        assetregistry.unregisterFactory(factory)
        self.assertEquals(
            None, assetregistry.getFactoryForMimetype(self.root, mimetype))
    
    def test_unregisterMimetype(self):
        factory = Document.manage_addDocument
        mimetype = 'application/x-test-mimetype-1'
        assetregistry.registerFactoryForMimetype(mimetype, factory, 'Silva')
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetype))
        assetregistry.unregisterMimetype(mimetype)
        self.assertEquals(
            None, assetregistry.getFactoryForMimetype(self.root, mimetype))
    
    def test_factoryLookupWhereExtensionIsNotInstalled(self):
        factory = Document.manage_addDocument
        mimetype1 = 'application/x-test-mimetype-1'
        assetregistry.registerFactoryForMimetype(mimetype1, factory, 'Silva')
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetype1))
        mimetype2 = 'application/x-test-mimetype-2'
        assetregistry.registerFactoryForMimetype(mimetype2, factory, 'SilvaDocument')
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetype2))        
        es = self.root.service_extensions
        es.uninstall('SilvaDocument')
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetype1))
        self.assertEquals(
            None, assetregistry.getFactoryForMimetype(self.root, mimetype2))
        es.install('SilvaDocument')
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetype1))
        self.assertEquals(
            factory, assetregistry.getFactoryForMimetype(self.root, mimetype2))
    
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AssetRegistryTestCase))
    return suite

# Copyright (c) 2002, 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_icon.py,v 1.4 2003/10/10 15:19:51 gotcha Exp $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from ZPublisher.HTTPRequest import FileUpload
from Globals import ImageFile

from StringIO import StringIO

from Products.Silva import Root
from Products.Silva.icon import *
from Products.Silva.interfaces import IAsset


class AdapterTest(SilvaTestCase.SilvaTestCase):

    def test_MetaTypeAdapter(self):
        a = MetaTypeAdapter(self.silva)
        self.assertEquals(a.getIconIdentifier(), ('meta_type', 'Silva Root'))
        self.assertRaises(AdaptationError, MetaTypeAdapter, "astring")


class R:
    pass
    
class RegistryTest(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        fields = R()
        fields.filename = 'afilename'
        fields.headers = {'content-type': 'application/mytype'}
        fields.file = StringIO("a nice pdf ;)")
        upload = FileUpload(fields)
        self.silva.manage_addProduct['Silva'].manage_addFile('fileasset',
            'a nice title', upload)
        fields = R()
        fields.filename = 'anoterfilename'
        fields.headers = {}
        fields.file = StringIO("just plain data")
        upload = FileUpload(fields)
        self.silva.manage_addProduct['Silva'].manage_addFile('datafile',
            'data file', upload)
    
    def test_registry(self):
        self.assertEquals(self.silva.fileasset.get_mime_type(),
            'application/mytype')
        r = registry
        #should not test internals but interface
        #self.assertEquals(r._get_module_from_context(Root.__dict__), 'Silva')
        #self.assertEquals(r._get_module_from_context(Zope.__dict__), 'Zope')
        r.registerAdapter(MetaTypeAdapter, 0)
        r.registerAdapter(SilvaFileAdapter, 10)
        #should not test internals but interface
        #self.assertEquals(len(r._adapters), 2)
        #self.assertEquals(r._adapters[0].priority, 10)
        #self.assertEquals(r._adapters[1].priority, 0)
        adapter = r.getAdapter(self.silva.fileasset)
        self.failUnless(isinstance(adapter, SilvaFileAdapter))
        adapter = r.getAdapter(self.silva)
        self.failUnless(isinstance(adapter, MetaTypeAdapter))
        
        r.registerIcon(('meta_type', 'Silva Root'),
            'www/members.png', Root.__dict__)
        r.registerIcon(('mime_type', 'application/octet-stream'),
            'www/silvafile.png', Root.__dict__)
        r.registerIcon(('mime_type', 'application/mytype'),
            'www/user.png', Root.__dict__)
            
        icon = r.getIcon(self.silva)
        self.assertEquals(icon, 'misc_/Silva/members.png')
        icon = r.getIcon(self.silva.fileasset)
        self.assertEquals(icon, 'misc_/Silva/user.png')
        icon = r.getIcon(self.silva.datafile)
        self.assertEquals(icon, 'misc_/Silva/silvafile.png')
        
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(AdapterTest))
        suite.addTest(unittest.makeSuite(RegistryTest))
        return suite
    

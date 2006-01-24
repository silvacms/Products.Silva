# Copyright (c) 2002-2006 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_icon.py,v 1.8 2006/01/24 16:13:33 faassen Exp $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from ZPublisher.HTTPRequest import FileUpload
from Globals import ImageFile

from StringIO import StringIO
from Products.Silva.icon import _IconRegistry
from Products.Silva import Root
from Products.Silva.interfaces import IAsset

class R:
    pass

class RegistryTest(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        fields = R()
        fields.filename = 'afilename.pdf'
        fields.headers = {}
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
            'application/pdf')
        r = _IconRegistry()
        
        r.registerIcon(('meta_type', 'Silva Root'),
            'www/members.png', Root.__dict__)
        r.registerIcon(('mime_type', 'application/octet-stream'),
            'www/silvafile.png', Root.__dict__)
        r.registerIcon(('mime_type', 'application/pdf'),
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
        suite.addTest(unittest.makeSuite(RegistryTest))
        return suite
    

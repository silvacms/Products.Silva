# Copyright (c) 2002, 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_mangle.py,v 1.2 2003/08/13 11:45:45 zagy Exp $

import Zope
Zope.startup()

import unittest
from StringIO import StringIO

from Products.Silva import mangle
from Products.Silva.interfaces import IAsset
from Products.Silva.tests.base import SilvaTestCase



class MangleIdTest(SilvaTestCase):

    def setUp(self):
        SilvaTestCase.setUp(self)
        self.folder = folder = self.addObject(self.silva, 'Folder', 'fold',
            title='fold', create_default=0)
        self.addObject(folder, 'SimpleContent', 'a_content',
            title='a_content')
        self.addObject(folder, 'File', 'an_asset', title='an_asset',
            file=StringIO("foobar"))
    
    def test_validate(self):
        id = mangle.Id(self.folder, 'some_id')
        self.assertEquals(id.validate(), id.OK)
        
        id = mangle.Id(self.folder, 'a_content')
        self.assertEqual(id.validate(), id.IN_USE_CONTENT)
   
        id = mangle.Id(self.folder, 'an_asset')
        self.assertEqual(id.validate(), id.IN_USE_ASSET)
   
        id = mangle.Id(self.folder, 'a_content', allow_dup=1)
        self.assertEqual(id.validate(), id.OK)
   
        id = mangle.Id(self.folder, 'an_asset', allow_dup=1)
        self.assertEqual(id.validate(), id.OK)
        
        id = mangle.Id(self.folder, 'service_foobar')
        self.assertEqual(id.validate(), id.RESERVED_PREFIX)
   
        id = mangle.Id(self.folder, '&*$()')
        self.assertEqual(id.validate(), id.CONTAINS_BAD_CHARS)
        
        id = mangle.Id(self.folder, 'index_html')
        self.assertEqual(id.validate(), id.RESERVED)
   
        id = mangle.Id(self.folder, 'index')
        self.assertEqual(id.validate(), id.OK)
   
        id = mangle.Id(self.folder, 'index', interface=IAsset)
        self.assertEqual(id.validate(), id.RESERVED)
   
        an_asset = self.folder.an_asset
        id = mangle.Id(self.folder, 'index', instance=an_asset)
        self.assertEqual(id.validate(), id.RESERVED)
    

class ManglePathTest(SilvaTestCase):

    def test_path(self):
        test_cases = [
            ('/silva/foo', '/silva/foo/bar', 'bar'),
            ('/silva/foo', '/silva/bar', '/silva/bar'),
            ('/silva/foo', '/bar', '/bar'),
           ]
        for case in test_cases:
            base_path, item_path, expected_result = case
            base_path = base_path.split('/')
            item_path = item_path.split('/')
            expected_result = expected_result.split('/')
            actual_result = mangle.Path(base_path, item_path)
            __traceback_info__ = case
            self.assertEquals(expected_result, actual_result)

    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MangleIdTest))
    suite.addTest(unittest.makeSuite(ManglePathTest))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
    

# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_file.py,v 1.1 2003/02/17 14:55:39 zagy Exp $

import unittest

import Zope
Zope.startup()
from Products.Silva import File


class FileTest(unittest.TestCase):
   
    def test_cookpath(self):
        
        self.assertEqual(File.cookPath("foo/bar/baz"), ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("/foo/bar/baz"), ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("foo/../bar/baz"), 
            ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("foo/bar//baz"), 
            ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("foo/bar/./baz"), 
            ('foo', 'bar', 'baz'))
        
    
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileTest))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
    

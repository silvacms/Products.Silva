# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_file.py,v 1.2 2003/10/10 18:04:45 faassen Exp $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase

from Products.Silva import File

class FileTest(SilvaTestCase.SilvaTestCase):
   
    def test_cookpath(self):
        
        self.assertEqual(File.cookPath("foo/bar/baz"), ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("/foo/bar/baz"), ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("foo/../bar/baz"), 
            ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("foo/bar//baz"), 
            ('foo', 'bar', 'baz'))
        self.assertEqual(File.cookPath("foo/bar/./baz"), 
            ('foo', 'bar', 'baz'))
    
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(FileTest))
        return suite

# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.7 $
import unittest
import Zope

from Products.Silva.tests import test_Versioning
from Products.Silva.tests import test_VersionedContent
from Products.Silva.tests import test_SilvaObject
from Products.Silva.tests import test_Container
from Products.Silva.tests import test_Publishable
from Products.Silva.tests import test_Ghost
from Products.Silva.tests import test_Copy
from Products.Silva.tests import test_Security
from Products.Silva.tests import test_CatalogedVersioning

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(test_Versioning.test_suite())
    suite.addTest(test_VersionedContent.test_suite())
    suite.addTest(test_SilvaObject.test_suite())
    suite.addTest(test_Container.test_suite())
    suite.addTest(test_Publishable.test_suite())
    suite.addTest(test_Ghost.test_suite())
    suite.addTest(test_Copy.test_suite())
    suite.addTest(test_Security.test_suite()) 
    #suite.addTest(test_CatalogedVersioning.test_suite()) 
    return suite

def main():
    unittest.TextTestRunner(verbosity=1).run(test_suite())

if __name__ == '__main__':
    main()
    

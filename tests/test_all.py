import unittest
import Zope

from Products.Silva.tests import test_Versioning
from Products.Silva.tests import test_VersionedContent
from Products.Silva.tests import test_SilvaObject
from Products.Silva.tests import test_Container
from Products.Silva.tests import test_Publishable
from Products.Silva.tests import test_Ghost

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(test_Versioning.test_suite())
    suite.addTest(test_VersionedContent.test_suite())
    suite.addTest(test_SilvaObject.test_suite())
    suite.addTest(test_Container.test_suite())
    suite.addTest(test_Publishable.test_suite())
    suite.addTest(test_Ghost.test_suite())
    return suite

def main():
    unittest.TextTestRunner(verbosity=1).run(test_suite())

if __name__ == '__main__':
    main()
    

# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $
import unittest
import Zope
#import ZODB
#import OFS.Application
from DateTime import DateTime
from Products.Silva import Versioning

class VersioningTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_workflow1(self):
        versioning = Versioning.Versioning()
        # no public version yet
        self.assertEqual(versioning.get_public_version(),
                         None)
        # no unapproved version yet
        self.assertEqual(versioning.get_unapproved_version(),
                         None)
        # no approved version yet
        self.assertEqual(versioning.get_approved_version(),
                         None)
        # create new version
        versioning.create_version('foo', DateTime() - 1, DateTime() + 1)
        # still no public version
        self.assertEqual(versioning.get_public_version(),
                         None)
        # there is an unapproved version now
        self.assertEqual(versioning.get_unapproved_version(),
                         'foo')
        # no approved version yet
        self.assertEqual(versioning.get_approved_version(),
                         None)
        # approve it
        versioning.approve_version()
        # public version is now foo, as datetime was set in the past
        self.assertEqual(versioning.get_public_version(),
                         'foo')
        self.assertEqual(versioning.get_unapproved_version(),
                         None)
        self.assertEqual(versioning.get_approved_version(),
                         None)
        # create new version
        versioning.create_version('bar', DateTime() - .5,
                                  DateTime() + 1)
        self.assertEqual(versioning.get_public_version(),
                         'foo')
        self.assertEqual(versioning.get_approved_version(),
                         None)
        self.assertEqual(versioning.get_unapproved_version(),
                         'bar')
        # approve bar
        versioning.approve_version()
        self.assertEqual(versioning.get_public_version(),
                         'bar')
        self.assertEqual(versioning.get_approved_version(),
                         None)
        self.assertEqual(versioning.get_unapproved_version(),
                         None)

    def test_workflow2(self):
        versioning = Versioning.Versioning()
        # no public version yet
        self.assertEqual(versioning.get_public_version(),
                         None)
        # no unapproved version yet
        self.assertEqual(versioning.get_unapproved_version(),
                         None)
        # no approved version yet
        self.assertEqual(versioning.get_approved_version(),
                         None)
        # create new version
        versioning.create_version('foo', DateTime() + 1, DateTime() + 2)
        # still no public version
        self.assertEqual(versioning.get_public_version(),
                         None)
        # there is an unapproved version now
        self.assertEqual(versioning.get_unapproved_version(),
                         'foo')
        # no approved version yet
        self.assertEqual(versioning.get_approved_version(),
                         None)
        # approve it
        versioning.approve_version()
        # public version is still not foo, as it is set to start in the
        # future
        self.assertEqual(versioning.get_public_version(),
                         None)
        self.assertEqual(versioning.get_unapproved_version(),
                         None)
        self.assertEqual(versioning.get_approved_version(),
                         'foo')
    
        # unapprove it
        versioning.unapprove_version()
        # change the time to something in the past, so it'll be published
        versioning.set_unapproved_version_publication_datetime(DateTime() - 0.1)
        # approve it
        versioning.approve_version()
        self.assertEqual(versioning.get_public_version(), 'foo')
        
    def test_workflow3(self):
        versioning = Versioning.Versioning()
 
        # create new version
        versioning.create_version('first', DateTime() - 1, DateTime() + 2)
        # approve it
        versioning.approve_version()
        # it should be public now, create new version
        versioning.create_version('second', DateTime() - 0.5, DateTime() + 2)
        self.assertEqual(versioning.get_public_version(), 'first')
        self.assertEqual(versioning.get_unapproved_version(), 'second')

    def test_workflow4(self):
        versioning = Versioning.Versioning()
 
        # create new version
        versioning.create_version('first', DateTime() + 1, DateTime() + 2)
        # approve it
        versioning.approve_version()
        # unapprove it again
        versioning.unapprove_version()
        # change datetime
        versioning.set_unapproved_version_publication_datetime(DateTime() - 1)
        # now approve it
        versioning.approve_version()
        # it should be public now
        self.assertEqual(versioning.get_public_version(), 'first')
        # create new version
        versioning.create_version('second', DateTime() - 0.5, DateTime() + 2)
        self.assertEqual(versioning.get_unapproved_version(), 'second')
        # approve it
        versioning.approve_version()
        # second should be public now
        self.assertEqual(versioning.get_public_version(), 'second')

    def test_workflow5(self):
        # test manual close
        versioning = Versioning.Versioning()
        # create new version, publish before now, expire after now
        versioning.create_version('first', DateTime() - 1, DateTime() + 2)
        # approve it
        versioning.approve_version()
        # should be published now, not expired yet
        # close public version
        versioning.close_version()
        self.assertEqual(versioning.get_previous_versions(), ['first'])
        self.assertEqual(versioning.get_last_closed_version(), 'first')
        # create a new version
        versioning.create_version('second', DateTime() - 1, DateTime() + 2)
        # approve and close it too
        versioning.approve_version()
        versioning.close_version()
        self.assertEqual(versioning.get_previous_versions(), ['first', 'second'])
        self.assertEqual(versioning.get_last_closed_version(), 'second')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersioningTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()


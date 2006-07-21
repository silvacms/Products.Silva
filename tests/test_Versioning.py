# Copyright (c) 2003-2006 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $
import SilvaTestCase
from Testing import ZopeTestCase

from DateTime import DateTime
from Products.Silva import Versioning
from OFS import SimpleItem

class ZODBVersioning(Versioning.Versioning,  SimpleItem.SimpleItem):
    # awful hack a versioning implementation which also may have a REQUEST associated
    # interestingly it works w/o having an acquisition parent, etc.

    # I hope you will not find this type in the add list of the ZMI ;-)
    meta_type='ZODB Hack Versioning'

    def reindex_object(self):
        """ needed, as this is called by a folders manage_afterAdd """
        pass


def manage_addZODBVersioning(self, id):
    object = ZODBVersioning(id, 'Test dummy')
    self._setObject(id, object)
    return ''
    

class VersioningTestCase(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
       self.REQUEST = self.root.REQUEST
       manage_addZODBVersioning(self.root, 'versioning')
       self.versioning = self.root.versioning

    def test_workflow1(self):
        versioning = self.versioning
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
        versioning = self.versioning

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
        versioning = self.versioning
 
        # create new version
        versioning.create_version('first', DateTime() - 1, DateTime() + 2)
        # approve it
        versioning.approve_version()
        # it should be public now, create new version
        versioning.create_version('second', DateTime() - 0.5, DateTime() + 2)
        self.assertEqual(versioning.get_public_version(), 'first')
        self.assertEqual(versioning.get_unapproved_version(), 'second')

    def test_workflow4(self):
        versioning = self.root.versioning

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
        versioning = self.versioning
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


    # XXX assume boolean values are 0 and 1 ... will fail for python2.2
    def _check_version_state(self, approved=0, approval_requested=0, published=0):
        # helper method to check consistency of the version state
        # XXX no good error messages if test fail
        self.assertEquals(approved, self.versioning.is_version_approved())
        self.assertEquals(approved and self.versioning.get_next_version() or None,
                          self.versioning.get_approved_version())
        self.assertEquals(published, self.versioning.is_version_published())
        # XXX cannot test this: get_next_version returns None
        # if there is only a published version (?)
        #self.assertEquals(published and self.versioning.get_next_version() or None,
        #                  self.versioning.get_public_version())
        self.assertEquals(approval_requested and not approved,
                          self.versioning.is_version_approval_requested())
        self.assertEquals((not approved) and self.versioning.get_next_version() or None,
                          self.versioning.get_unapproved_version())
        

    def test_workflow6(self):
        true=1
        # test request for approval
        self._check_version_state()
        self.versioning.create_version('0', DateTime() + 10, None)
        self._check_version_state()
        self.versioning.request_version_approval('foo')
        self._check_version_state(approval_requested=true)
        self.assertEquals(ZopeTestCase.user_name, self.versioning.get_approval_requester())
        self.assertEquals('foo',
                          self.versioning.get_approval_request_message())
        self.versioning.withdraw_version_approval('Withdraw message')
        self._check_version_state()
        self.versioning.request_version_approval('Request message')
        self._check_version_state(approval_requested=true)
        self.versioning.approve_version()
        self._check_version_state(approved=true)

        
        # just check, if request for approval could break unaproval
        # or close later, though this is unreasonable
        self.versioning.unapprove_version()
        self._check_version_state()
        self.versioning.approve_version()
        self._check_version_state(approved=true)
        self.versioning.set_approved_version_publication_datetime(DateTime()-1)
        self.versioning.close_version()
        self._check_version_state()
        self.versioning.create_version('1', DateTime() + 1, None)
        self._check_version_state()

        

    def test_illegal_request_approval(self):
        # test if all kind of VersioningError are actually raised
        try:
            self.versioning.request_version_approval('Request message')
            self.fail(msg="cannot request for approval without version")
        except Versioning.VersioningError:
            pass
        
        self.versioning.create_version('first', DateTime() + 10, None)
        self.versioning.request_version_approval('Request message')
        try:
            self.versioning.request_version_approval('Request message')
            self.fail(msg="cannot request for approval twice")
        except Versioning.VersioningError:
            pass

        self.versioning.withdraw_version_approval('Withdraw message')
        try:
            self.versioning.withdraw_version_approval('Withdraw message')
            self.fail(msg="cannot withdraw request for approval twice")
        except Versioning.VersioningError:
            pass

        self.versioning.approve_version()
        try:
            self.versioning.request_version_approval('Request message')
            self.fail(msg="cannot request for approval after approving version")
        except Versioning.VersioningError:
            pass
        try:
            self.versioning.withdraw_version_approval('Withdraw message')
            self.fail(msg="cannot withdraw request for approval after approving version")
        except Versioning.VersioningError:
            pass

        self.versioning.unapprove_version()
        try:
            self.versioning.withdraw_version_approval('Withdraw message')
            self.fail(msg="cannot withdraw request for approval after approving and unapproving version")
        except Versioning.VersioningError:
            pass
        self.versioning.request_version_approval('Request message')
        self._check_version_state(approval_requested=1)

        # XXX check publish state here ? shoud be in workflow6?
        self.versioning.set_unapproved_version_publication_datetime(DateTime()-1)
        self.versioning.approve_version()
        self._check_version_state(published=1)
        self.versioning.close_version()
        
        try:
            self.versioning.request_version_approval('Request message')
            self.fail(msg="cannot request for approval after closing version")
        except Versioning.VersioningError:
            pass
        try:
            self.versioning.withdraw_version_approval('Withdraw message')
            self.fail(msg="cannot withdraw request for approval after closing version")
        except Versioning.VersioningError:
            pass


    def _test_workflow7(self):
        # reopen a closed version
 
        # create new version
        self.versioning.create_version('first', DateTime() - 1, DateTime() + 2)
        # approve and close it
        self.versioning.set_unapproved_version_publication_datetime(DateTime()-1)
        self.versioning.approve_version()
        self.versioning.close_version()
        self._check_version_state()
        
        self.versioning.approve_version()
        self._check_version_state(approved=1)
        # did not create an new version
        self.assertEquals('first', self.versioning.get_approved_version())
       

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersioningTestCase, 'test'))
    return suite
    
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersioningTestCase))
    return suite


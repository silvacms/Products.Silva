# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from DateTime import DateTime

import SilvaTestCase


class PublishableTestCase(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.document = self.add_document(self.root, 'document', 'Document')
        self.folder = self.add_folder(self.root, 'folder', 'Folder',
                                      policy_name='Silva Document')
        self.subdoc = self.add_document(self.folder, 'subdoc', 'Document')

    def test_is_published(self):
        self.assert_(not self.document.is_published())
        self.assert_(not self.folder.is_published())
        self.document.set_unapproved_version_publication_datetime(
            DateTime() - 1)
        self.document.approve_version()
        self.assert_(self.document.is_published())
        # folder is published if its default is published
        self.assert_(not self.folder.is_published())
        self.folder.get_default().set_unapproved_version_publication_datetime(
            DateTime() - 1)
        self.folder.get_default().approve_version()
        self.assert_(self.folder.get_default().is_published())
        self.assert_(self.folder.is_published())
        
    def test_is_published2(self):
        # folder is *not* published if any of its contents is published;
        # this has changed with Silva 1.6
        self.assert_(not self.folder.is_published())
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.subdoc.approve_version()
        self.assert_(not self.folder.is_published())

    def test_is_published3(self):
        # first publish default
        self.folder.get_default().set_unapproved_version_publication_datetime(
            DateTime() - 1)
        self.folder.get_default().approve_version()
        self.assert_(self.folder.is_published())
        # now close default
        self.folder.get_default().close_version()
        self.assert_(not self.folder.is_published())
        # now remove default
        self.folder.action_delete(['index'])
        self.assert_(not self.folder.is_published())
        
    def approve_document(self):
        self.document.set_unapproved_version_publication_datetime(
            DateTime() - 1)
        self.document.approve_version()

    def approve_sub_document(self):
        self.folder.get_default().approve_version()
    
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PublishableTestCase))
    return suite

# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.5 $
import unittest
import Zope
from DateTime import DateTime
from Products.Silva.Versioning import VersioningError

class PublishableTestCase(unittest.TestCase):
    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = self.connection.root()['Application']
        self.root.manage_addProduct['Silva'].manage_addRoot('root', 'Root')
        self.sroot = self.root.root
        add = self.sroot.manage_addProduct['Silva']
        add.manage_addDocument('document', 'Document')
        add.manage_addFolder('folder', 'Folder')
        self.document = self.sroot.document
        self.folder = self.sroot.folder
        self.folder.manage_addProduct['Silva'].manage_addDocument('subdoc', 'Document')
        self.subdoc = self.folder.subdoc
        
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

    def test_activation_unpublished(self):
        # we can deactivate/activate something that is unpublished
        self.assert_(self.document.is_active())
        self.assert_(self.document.can_deactivate())
        self.document.deactivate()
        self.assert_(not self.document.is_active())
        self.assert_(self.document.can_activate())
        self.document.activate()
        self.assert_(self.document.is_active())

    def test_activation_unpublished2(self):
        # we can't approve something that is deactivated
        self.assert_(self.document.is_active())
        self.document.deactivate()
        self.assert_(not self.document.is_active())
        self.assert_(self.document.can_activate())
        self.failUnlessRaises(VersioningError, self.approve_document)

    def test_activation_published(self):
        # can't deactivate something that is published
        self.document.set_unapproved_version_publication_datetime(
            DateTime() - 1)
        self.document.approve_version()
        self.assert_(not self.document.can_deactivate())
        # should do nothing
        self.document.deactivate()
        self.assert_(self.document.is_active())
    
    def test_activation_closed(self):
        # can deactivate something that is closed (and not published)
        self.document.set_unapproved_version_publication_datetime(
            DateTime() - 1)
        self.document.approve_version()
        self.document.close_version()
        self.assert_(self.document.can_deactivate())
        self.document.deactivate()
        self.assert_(not self.document.is_active())
        self.document.activate()
        self.assert_(self.document.is_active())

    def test_activation_approved(self):
        # if we deactivate something that is approved, unapprove it first
        self.document.set_unapproved_version_publication_datetime(
            DateTime() + 1)
        self.document.approve_version()
        self.assert_(self.document.can_deactivate())
        self.document.deactivate()
        self.assert_(not self.document.is_version_approved())

    def test_activation_approved2(self):
        # if we deactivate a folder unapprove everything inside
        self.folder.manage_addProduct['Silva'].manage_addFolder('subfolder', 'Subfolder')
        subfolder = self.folder.subfolder
        subfolder.manage_addProduct['Silva'].manage_addDocument('subsubdoc', 'Subsubdoc')
        subsubdoc = subfolder.subsubdoc
        # we can deactivate it still
        self.assert_(self.folder.can_deactivate())
        # but now we approve something inside
        subsubdoc.set_unapproved_version_publication_datetime(
            DateTime() + 1)
        subsubdoc.approve_version()
        # we can still deactivate it
        self.assert_(self.folder.can_deactivate())
        # deactivate it
        self.folder.deactivate()
        # the subsubdoc should be unapproved
        self.assert_(not subsubdoc.is_version_approved())
        self.assert_(not subsubdoc.is_version_published())
        self.assert_(subsubdoc.get_unapproved_version())
        
    def test_folder_activation(self):
        # we can deactivate folder if it is not published
        self.folder.deactivate()
        self.assert_(not self.folder.is_active())
        self.folder.activate()
        self.assert_(self.folder.is_active())
        # we can't deactivate folder if something inside is published
        self.folder.get_default().set_unapproved_version_publication_datetime(
            DateTime() - 1)
        self.folder.get_default().approve_version()
        self.assert_(self.folder.is_published())
        self.assert_(not self.folder.can_deactivate())
        self.folder.deactivate()
        self.assert_(self.folder.is_active())
    
    def test_folder_activation2(self):
        # we can't publish something in an inactive folder
        self.folder.deactivate()
        self.folder.get_default().set_unapproved_version_publication_datetime(
            DateTime() - 1)
        self.assert_(not self.folder.get_default().can_approve())
        self.assertRaises(VersioningError, self.approve_sub_document)

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
        # folder is published if any of its contents if published
        self.assert_(not self.folder.is_published())
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.subdoc.approve_version()
        self.assert_(self.folder.is_published())

    def test_is_published3(self):
        # first publish default
        self.folder.get_default().set_unapproved_version_publication_datetime(DateTime() - 1)
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
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PublishableTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()

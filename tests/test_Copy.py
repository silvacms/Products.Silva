# Copyright (c) 2003-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $
import SilvaTestCase
from Testing import ZopeTestCase

from Products.Silva import Folder, Root
from DateTime import DateTime

# manage_main hacks to copy succeeds
# the original manage_main needs a request['URL1']
# which is not set up in the test request
#Root.Root.manage_main = lambda *foo, **bar: None
#Folder.Folder.manage_main = lambda *foo, **bar: None

class NoSetupCopyTestCase(SilvaTestCase.SilvaTestCase):

    def _query(self, **kwargs):
        return self.root.service_catalog(**kwargs)

    def test_cut1(self):
        folder = self.add_folder(
            self.root, 'folder', 'Folder', policy_name='Silva AutoTOC')
        
        subdoc = self.add_document(folder, 'subdoc', 'Subdoc')
    
        folder2 = self.add_folder(
            self.root, 'folder2', 'Folder2', policy_name='Silva AutoTOC')
        
        self.assertEquals(len([b.getPath() for b in
                               self._query(path='/root/folder')]),
                          2)
        
        self.root.action_cut(['folder'], self.app.REQUEST)
        self.root.folder2.action_paste(self.app.REQUEST)
    
        self.assertEquals(
            [b.getPath() for b in self._query(path='/root/folder')], [])
        self.assertEquals(len([b.getPath() for b in
                               self._query(path='/root/folder2/folder')]),
                          2)

    def test_check_ordered_ids(self):
        doc = self.add_document(self.root, 'mydoc', 'My Document')
        self.assertEquals(self.root.get_ordered_publishables(), [doc])
        self.root.action_delete(['mydoc'])
        self.assertEquals(self.root.get_ordered_publishables(), [])

    def test_remove_root(self):
        folder = self.add_folder(
            self.root, 'folder', 'Folder', policy_name='Silva AutoTOC')
       
        # Just to make sure that this works
        self.app.manage_delObjects([self.root.getId()])
        self.assert_(self.root.getId() not in self.app.objectIds())

class CopyTestCase(SilvaTestCase.SilvaTestCase):
    """Test cut/copy/test/delete.
    """
    def afterSetUp(self):
        self.doc1 = doc1 = self.add_document(self.root, 'doc1', 'Doc1')
        self.doc2 = doc2 = self.add_document(self.root, 'doc2', 'Doc2')
        self.doc3 = doc3 = self.add_document(self.root, 'doc3', 'Doc3')
        self.folder4 = folder4 = self.add_folder(
            self.root, 'folder4', 'Folder4', policy_name='Silva AutoTOC')
        self.folder5 = folder5 = self.add_folder(
            self.root, 'folder5', 'Folder5', policy_name='Silva AutoTOC')
        self.folder6 = folder6 = self.add_folder(
            self.root, 'folder6', 'Folder6', policy_name='Silva Document')
        self.subdoc = subdoc = self.add_document(
            folder4, 'subdoc', 'Subdoc')
        self.subfolder = subfolder = self.add_folder(
            folder4, 'subfolder', 'Subfolder', policy_name='Silva AutoTOC')
        self.subsubdoc = subsubdoc = self.add_document(
            subfolder, 'subsubdoc', 'Subsubdoc')

    def test_copy1(self):
        self.root.action_copy(['doc1'], self.app.REQUEST)
        # now do the paste action
        self.root.action_paste(self.app.REQUEST)
        # should have a copy now with same title
        self.assertEquals('Doc1', self.root.copy_of_doc1.get_title_editable())

    def test_copy2(self):
        # approve version
        self.doc1.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.doc1.approve_version()
        self.assert_(self.root.doc1.is_version_approved())
        # copy of approved version should not be approved
        self.root.action_copy(['doc1'], self.app.REQUEST)
        self.root.action_paste(self.app.REQUEST)
        self.assert_(not self.root.copy_of_doc1.is_version_approved())
        # original *should* be approved
        self.assert_(self.root.doc1.is_version_approved())
       
    def test_copy3(self):
        # approve & publish version
        self.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc1.approve_version()
        self.assert_(self.root.doc1.is_version_published())
        # copy of approved version should not be approved
        self.root.action_copy(['doc1'], self.app.REQUEST)
        self.root.action_paste(self.app.REQUEST)
        self.assert_(not self.root.copy_of_doc1.is_version_published())
        # original *should* be published
        self.assert_(self.root.doc1.is_version_published())

    def test_copy4(self):
        # approve
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.subdoc.approve_version()
        self.assert_(self.subdoc.is_version_approved())
        # now copy the folder subdoc is in
        self.root.action_copy(['folder4'], self.app.REQUEST)
        self.root.action_paste(self.app.REQUEST)
        # the thing inside it should not be approved
        self.assert_(not self.root.copy_of_folder4.subdoc.is_version_approved())
        # original *should* be approved
        self.assert_(self.subdoc.is_version_approved())
       
    def test_copy5(self):
        # approve & publish
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.subdoc.approve_version()
        self.assert_(self.subdoc.is_version_published())
        # now copy the folder subdoc is in
        self.root.action_copy(['folder4'], self.app.REQUEST)
        self.root.action_paste(self.app.REQUEST)
        # the thing inside it should not be published
        self.assert_(not self.root.copy_of_folder4.subdoc.is_version_published())
        # original *should* be published
        self.assert_(self.subdoc.is_version_published())

    def test_copy6(self):
        # approve & publish
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.subdoc.approve_version()
        self.assert_(self.subdoc.is_version_published())
        # now copy the folder subdoc is in
        self.root.action_copy(['folder4'], self.app.REQUEST)
        # into folder5
        self.root.folder5.action_paste(self.app.REQUEST)
        # the thing inside it should not be published
        self.assert_(not self.root.folder5.folder4.subdoc.is_version_published())
        # original *should* be published
        self.assert_(self.subdoc.is_version_published())

    def test_copy7(self):
        # test for issue 92: pasted ghosts have unknown author
        self.add_ghost(self.root.folder4, 'ghost6', '/root/doc1')
        self.failUnless(self.root.folder4.ghost6)
       # gotcha this makes the tests pass but I am not sure it is the desired
       # functionality : test was failing because a ghost on a private doc does
       # not get metadata !
       # approve & publish version
        self.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc1.approve_version()
        self.assert_(self.root.doc1.is_version_published())
       # gotcha    
        self.root.folder4.ghost6.sec_update_last_author_info()        
        self.assertEquals(
            ZopeTestCase.user_name,
            self.root.folder4.ghost6.sec_get_last_author_info().fullname())
        # copy ghost to folder 4 and check author
       # XXX maybe we should rename the user inbetween ?
        self.root.folder4.action_copy(['ghost6'], self.app.REQUEST)
        self.root.folder5.action_paste(self.app.REQUEST)
        self.assertEquals(
            ZopeTestCase.user_name,
            self.root.folder5.ghost6.sec_get_last_author_info().fullname())
        # move ghost to root and check author        
        self.root.folder4.action_cut(['ghost6'], self.app.REQUEST)
        self.root.action_paste(self.app.REQUEST)
        self.assertEquals(
            ZopeTestCase.user_name,
            self.root.ghost6.sec_get_last_author_info().fullname())
        

    def test_copy8(self):
        # special test for testing rename behaviour
        # first create a copy of doc1 and paste it, the new id will be
        # 'copy_of_doc1'
        # first publish the doc to make it more exciting ;)
        self.doc1.set_unapproved_version_publication_datetime(DateTime())
        self.doc1.approve_version()
        self.root.action_copy(['doc1'], self.app.REQUEST)
        self.root.action_paste(self.app.REQUEST)
        self.assert_(hasattr(self.root, 'copy_of_doc1'))

       # now copy the object again and test the new id, should be
       # 'copy2_of_doc1' according to Zope 2.7.4+, used to be
       # 'copy_of_copy_of_doc1'
        self.root.action_copy(['copy_of_doc1'], self.app.REQUEST)
        from OFS.CopySupport import _cb_decode # HACK
        self.root.action_paste(self.app.REQUEST)
       # this fails in Zope < 2.7.4
        self.assert_(hasattr(self.root, 'copy2_of_doc1'))
        self.assertEquals(self.root.copy2_of_doc1.get_editable(), None)
        self.assertEquals(self.root.copy2_of_doc1.get_viewable(), None)
        self.assert_(self.root.copy2_of_doc1.get_last_closed() != None)

    def test_cut1(self):
       # try to cut object to paste it to the same folder
        self.root.action_cut(['doc1'], self.app.REQUEST)
        self.root.action_paste(self.app.REQUEST)
        self.assert_(hasattr(self.root, 'doc1'))

    def test_cut2(self):
        # try to cut object and paste it into another folder
        self.root.action_cut(['doc1'], self.app.REQUEST)
        self.root.folder4.action_paste(self.app.REQUEST)
        self.assert_(not hasattr(self.root, 'doc1'))
        self.assert_(hasattr(self.root.folder4, 'doc1'))

    def test_cut3(self):
        # try to cut folder and paste it into another folder
        self.root.action_cut(['folder4'], self.app.REQUEST)
        self.root.folder5.action_paste(self.app.REQUEST)
        self.assert_(not hasattr(self.root, 'folder4'))
        self.assert_(hasattr(self.root.folder5, 'folder4'))

    def test_cut4(self):
        # try to cut and paste folder to this folder again
        self.root.action_cut(['folder4'], self.app.REQUEST)
        self.root.action_paste(self.app.REQUEST)
        self.assert_(hasattr(self.root, 'folder4'))

    def test_cut5(self):
       # try to cut an approved content
       # should lead to an empty clipboard
        self.root.doc1.set_unapproved_version_publication_datetime(
            DateTime() - 1)
        self.root.doc1.approve_version()
        self.root.action_cut(['doc1'], self.app.REQUEST)
        self.root.folder4.action_paste(self.app.REQUEST)
        self.assert_(hasattr(self.root.aq_explicit, 'doc1'),
                     msg='doc1 should be still in root folder')
        self.assert_(not hasattr(self.root.folder4.aq_explicit, 'doc1'),
                     msg='doc1 should not be pasted in folder4')

    # should add unit tests for cut-pasting approved content
    # could occur if content is approved after its put on clipboard..

    def test_cut6(self):
       # try to cut a content, approve it and paste it later on
       # (should lead to an error at paste time, for now nothing happens)
        self.root.action_cut(['doc1'], self.app.REQUEST)
        self.root.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.root.doc1.approve_version()
        self.assert_(self.root.doc1.is_published())
        self.root.folder4.action_paste(self.app.REQUEST)
        self.assert_(hasattr(self.root.aq_explicit, 'doc1'),
                     msg='doc1 should be still in root folder')
        self.assert_(not hasattr(self.root.folder4.aq_explicit, 'doc1'),
                     msg='doc1 should not be pasted in folder4')

    def test_delete1(self):
       # just delete doc1, it should work
        self.assert_(self.root.is_delete_allowed('doc1'))
        self.root.action_delete(['doc1'])
        self.assert_(not hasattr(self.root, 'doc1'))

    def test_delete2(self):
       # just delete folder4, it should work
        self.assert_(self.root.is_delete_allowed('folder4'))
        self.root.action_delete(['folder4'])
        self.assert_(not hasattr(self.root, 'folder4'))
       
    def test_delete3(self):
       # make doc1 approved
        self.doc1.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.doc1.approve_version()
        self.assert_(self.doc1.is_approved())
       # now try to delete it (shouldn't be possible)
        self.assert_(not self.root.is_delete_allowed('doc1'))
        self.root.action_delete(['doc1'])
       # should still be there
        self.assert_(hasattr(self.root, 'doc1'))
       
    def test_delete4(self):
       # make doc1 approved & published
        self.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc1.approve_version()
       # now try to delete it (shouldn't be possible)
        self.assert_(not self.root.is_delete_allowed('doc1'))
        self.root.action_delete(['doc1'])
       # should still be there
        self.assert_(hasattr(self.root, 'doc1'))

    def test_delete5(self):
       # approve
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.subdoc.approve_version()
        self.assert_(not self.root.is_delete_allowed('folder4'))
        self.root.action_delete(['folder4'])
       # should still be there, as it contains an approved subdoc
        self.assert_(hasattr(self.root, 'folder4'))

    def test_delete6(self):
       # approve & published
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.subdoc.approve_version()
        self.assert_(not self.root.is_delete_allowed('folder4'))
        self.root.action_delete(['folder4'])
       # should still be there, as it contains a published subdoc
        self.assert_(hasattr(self.root, 'folder4'))

    def test_delete7(self):
       # delete folder without default doc
        self.folder4.action_delete(['index'])
        self.assert_(not hasattr(self.folder4.aq_explicit, 'index'))
        self.root.action_delete(['folder4'])
        self.assert_(not hasattr(self.root, 'folder4'))

    def test_delete8(self):
       # delete folder with default doc
        self.folder6.index.set_unapproved_version_publication_datetime(DateTime())
        self.folder6.index.approve_version()
        self.root.action_delete(['folder6'])
        self.assert_(hasattr(self.root.aq_explicit, 'folder6'))
        self.folder6.index.close_version()
        self.root.action_delete(['folder6'])
        self.assert_(not hasattr(self.root.aq_explicit, 'folder6'))

    def test_rename1(self):
        self.root.action_rename('doc1', 'docrenamed')
        self.assert_(not hasattr(self.root, 'doc1'))
        self.assert_(hasattr(self.root, 'docrenamed'))

    def test_rename2(self):
        self.doc1.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.doc1.approve_version()
        self.root.action_rename('doc1', 'docrenamed')
        self.assert_(hasattr(self.root, 'doc1'))
        self.assert_(not hasattr(self.root, 'docrenamed'))

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CopyTestCase))
    suite.addTest(unittest.makeSuite(NoSetupCopyTestCase))
    return suite


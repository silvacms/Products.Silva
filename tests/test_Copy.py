# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase

from Products.Silva import Folder, Ghost
from Products.SilvaDocument import Document
from DateTime import DateTime
from Products.ParsedXML.ParsedXML import ParsedXML
import ZPublisher
from AccessControl import getSecurityManager

# Awful hack
def _getCopyParsedXML(self, container):
    return ParsedXML(self.id, self.index_html())

def _getCopyDocument(self, container):
    # really really ugly..why doesn't copy work out of the box oh why..
    result = Document.Document(self.id, self.get_title())
    result = result.__of__(container)
    cb = self.manage_copyObjects(self.objectIds())
    result.manage_pasteObjects(cb)
    result._unapproved_version = self._unapproved_version
    result._approved_version = self._approved_version
    result._public_version = self._public_version
    result._previous_versions = self._previous_versions 
    return result

def _getCopyFolder(self, container):
    # very ugly as well. :)
    result = Folder.Folder(self.id, self.get_title())
    result = result.__of__(container)
    cb = self.manage_copyObjects(self.objectIds())
    result.manage_pasteObjects(cb)
    return result

def _getCopyGhost(self, container):
    # ghost need their own monkeypatch, too
    result = Ghost.Ghost(self.id)
    result.set_title(self.get_title())
    result = result.__of__(container)
    cb = self.manage_copyObjects(self.objectIds())
    result.manage_pasteObjects(cb)
    result._unapproved_version = self._unapproved_version
    result._approved_version = self._approved_version
    result._public_version = self._public_version
    result._previous_versions = self._previous_versions 
    return result

def _getCopyGhostVersion(self, container):
    # ghost version want a monkeypatch, too
    result = Ghost.GhostVersion(self.id)
    result = result.__of__(container)
    return result

def _verifyObjectPaste(self, ob):
    return

class CopyTestCase(SilvaTestCase.SilvaTestCase):
    """Test cut/copy/test/delete.
    """
    def afterSetUp(self):
        Document.Document._getCopy = _getCopyDocument
        ParsedXML._getCopy = _getCopyParsedXML
        Folder.Folder._getCopy = _getCopyFolder
        Folder.Folder._verifyObjectPaste = _verifyObjectPaste
        Document.Document._verifyObjectPaste = _verifyObjectPaste
        Ghost.Ghost._getCopy = _getCopyGhost
        Ghost.GhostVersion._getCopy = _getCopyGhostVersion
        Ghost.Ghost._verifyObjectPaste = _verifyObjectPaste
        
        self.REQUEST = self.root.REQUEST
        self.root.REQUEST['URL1'] = ''

        # dummy manage_main so that copy succeeds
        self.root.manage_main = lambda *foo, **bar: None
        self.doc1 = doc1 = self.add_document(self.root, 'doc1', 'Doc1')
        self.doc2 = doc2 = self.add_document(self.root, 'doc2', 'Doc2')
        self.doc3 = doc3 = self.add_document(self.root, 'doc3', 'Doc3')
        self.folder4 = folder4 = self.add_folder(self.root,
                          'folder4', 'Folder4')
        self.folder4.manage_main = lambda *foo, **bar: None
        self.folder5 = folder5 = self.add_folder(self.root,
                          'folder5', 'Folder5')
        self.folder5.manage_main = lambda *foo, **bar: None
        self.subdoc = subdoc = self.add_document(folder4,
                          'subdoc', 'Subdoc')
        self.subfolder = subfolder = self.add_folder(folder4,
                          'subfolder', 'Subfolder')
        self.subsubdoc = subsubdoc = self.add_document(subfolder,
                          'subsubdoc', 'Subsubdoc')
        self.setRoles(['Manager'])

    def test_copy1(self):
        self.root.action_copy(['doc1'], self.REQUEST)
        get_transaction().commit(1)
        # now do the paste action
        self.root.action_paste(self.REQUEST)
        get_transaction().commit(1)
        # should have a copy now with same title
        self.assertEquals('Doc1', self.root.copy_of_doc1.get_title())

    def test_copy2(self):
        # approve version
        self.doc1.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.doc1.approve_version()
        self.assert_(self.root.doc1.is_version_approved())
        # copy of approved version should not be approved
        self.root.action_copy(['doc1'], self.REQUEST)
        self.root.action_paste(self.REQUEST)
        self.assert_(not self.root.copy_of_doc1.is_version_approved())
        # original *should* be approved
        self.assert_(self.root.doc1.is_version_approved())
        
    def test_copy3(self):
        # approve & publish version
        self.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc1.approve_version()
        self.assert_(self.root.doc1.is_version_published())
        # copy of approved version should not be approved
        self.root.action_copy(['doc1'], self.REQUEST)
        self.root.action_paste(self.REQUEST)
        self.assert_(not self.root.copy_of_doc1.is_version_published())
        # original *should* be published
        self.assert_(self.root.doc1.is_version_published())
        
    def test_copy4(self):
        # approve
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.subdoc.approve_version()
        self.assert_(self.subdoc.is_version_approved())
        # now copy the folder subdoc is in
        self.root.action_copy(['folder4'], self.REQUEST)
        self.root.action_paste(self.REQUEST)
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
        self.root.action_copy(['folder4'], self.REQUEST)
        self.root.action_paste(self.REQUEST)
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
        self.root.action_copy(['folder4'], self.REQUEST)
        # into folder5
        print self.root.folder5
        get_transaction().commit(1)
        self.root.folder5.action_paste(self.REQUEST)
        get_transaction().commit(1)
        # the thing inside it should not be published
        self.assert_(not self.root.folder5.folder4.subdoc.is_version_published())
        # original *should* be published
        self.assert_(self.subdoc.is_version_published())


    def test_copy7(self):
        # test for issue 92: pasted ghosts have unknown author
        self.add_ghost(self.root.folder4, 'ghost6', 'Test Ghost')
        self.root.folder4.ghost6.sec_update_last_author_info()
        self.assertEquals('TestUser', self.root.folder4.ghost6.sec_get_last_author_info().fullname())
        # copy ghost to folder 4 and check author
        # XXX maybe we should rename the user inbetween ?
        self.root.folder4.action_copy(['ghost6'], self.REQUEST)
        self.root.folder5.action_paste(self.REQUEST)
        self.assertEquals('TestUser', self.root.folder5.ghost6.sec_get_last_author_info().fullname())
        # move ghost to root and check author        
        self.root.folder4.action_cut(['ghost6'], self.REQUEST)
        self.root.action_paste(self.REQUEST)
        self.assertEquals('TestUser', self.root.ghost6.sec_get_last_author_info().fullname())
        

    def test_cut1(self):
        # try to cut object to paste it to the same folder
        self.root.action_cut(['doc1'], self.REQUEST)
        self.root.action_paste(self.REQUEST)
        self.assert_(hasattr(self.root, 'doc1'))

    def test_cut2(self):
        # try to cut object and paste it into another folder
        self.root.action_cut(['doc1'], self.REQUEST)
        self.root.folder4.action_paste(self.REQUEST)
        self.assert_(not hasattr(self.root, 'doc1'))
        self.assert_(hasattr(self.root.folder4, 'doc1'))

    def test_cut3(self):
        # try to cut folder and paste it into another folder
        self.root.action_cut(['folder4'], self.REQUEST)
        self.root.folder5.action_paste(self.REQUEST)
        self.assert_(not hasattr(self.root, 'folder4'))
        self.assert_(hasattr(self.root.folder5, 'folder4'))

    def test_cut4(self):
        # try to cut and paste folder to this folder again
        self.root.action_cut(['folder4'], self.REQUEST)
        self.root.action_paste(self.REQUEST)
        self.assert_(hasattr(self.root, 'folder4'))

    def test_cut5(self):
        # try to cut an approved content
        # should lead to an empty clipboard
        self.root.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.root.doc1.approve_version()
        self.root.action_cut(['doc1'], self.REQUEST)
        self.root.folder4.action_paste(self.REQUEST)
        self.assert_(hasattr(self.root.aq_explicit, 'doc1'),
                     msg='doc1 should be still in root folder')
        self.assert_(not hasattr(self.root.folder4.aq_explicit, 'doc1'),
                     msg='doc1 should not be pasted in folder4')

    # should add unit tests for cut-pasting approved content
    # could occur if content is approved after its put on clipboard..

    def test_cut6(self):
        # try to cut a content, approve it and paste it later on
        # (should lead to an error at paste time, for now nothing happens)
        self.root.action_cut(['doc1'], self.REQUEST)
        self.root.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.root.doc1.approve_version()
        self.assert_(self.root.doc1.is_published())
        self.root.folder4.action_paste(self.REQUEST)
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

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(CopyTestCase))
        return suite


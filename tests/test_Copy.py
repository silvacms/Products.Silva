# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.18 $
import unittest
import Zope
Zope.startup()
from Products.Silva import Document, Folder, Ghost
from Testing import makerequest
from DateTime import DateTime
from Products.ParsedXML.ParsedXML import ParsedXML
import ZPublisher
from test_SilvaObject import hack_create_user

def add_helper(object, typename, id, title):
    getattr(object.manage_addProduct['Silva'],
            'manage_add%s' % typename)(id, title)
    return getattr(object, id)

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

class CopyTestCase(unittest.TestCase):
    """Test cut/copy/test/delete.
    """
    def setUp(self):
        Document.Document._getCopy = _getCopyDocument
        ParsedXML._getCopy = _getCopyParsedXML
        Folder.Folder._getCopy = _getCopyFolder
        Folder.Folder._verifyObjectPaste = _verifyObjectPaste
        Document.Document._verifyObjectPaste = _verifyObjectPaste
        Ghost.Ghost._getCopy = _getCopyGhost
        Ghost.GhostVersion._getCopy = _getCopyGhostVersion
        Ghost.Ghost._verifyObjectPaste = _verifyObjectPaste
        
        get_transaction().begin()
        self.connection = Zope.DB.open()
        try:
            self.root = makerequest.makerequest(self.connection.root()
                                                ['Application'])
            self.root.REQUEST['URL1'] = ''
            self.REQUEST = self.root.REQUEST
            # awful hack: add a user who may own the 'index'
            # of the test containers
            hack_create_user(self.root)
            self.sroot = sroot = add_helper(self.root, 'Root', 'root', 'Root')

            # dummy manage_main so that copy succeeds
            self.sroot.manage_main = lambda *foo, **bar: None
            self.doc1 = doc1 = add_helper(sroot, 'Document', 'doc1', 'Doc1')
            self.doc2 = doc2 = add_helper(sroot, 'Document', 'doc2', 'Doc2')
            self.doc3 = doc3 = add_helper(sroot, 'Document', 'doc3', 'Doc3')
            self.folder4 = folder4 = add_helper(sroot,
                              'Folder', 'folder4', 'Folder4')
            self.folder4.manage_main = lambda *foo, **bar: None
            self.folder5 = folder5 = add_helper(sroot,
                              'Folder', 'folder5', 'Folder5')
            self.folder5.manage_main = lambda *foo, **bar: None
            self.subdoc = subdoc = add_helper(folder4,
                              'Document', 'subdoc', 'Subdoc')
            self.subfolder = subfolder = add_helper(folder4,
                              'Folder', 'subfolder', 'Subfolder')
            self.subsubdoc = subsubdoc = add_helper(subfolder,
                              'Document', 'subsubdoc', 'Subsubdoc')
        except:
            self.tearDown()
            raise
          
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()
        
    def test_copy1(self):
        self.sroot.action_copy(['doc1'], self.REQUEST)
        # now do the paste action
        self.sroot.action_paste(self.REQUEST)
        # should have a copy now with same title
        self.assertEquals('Doc1', self.sroot.copy_of_doc1.get_title())

    def test_copy2(self):
        # approve version
        self.doc1.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.doc1.approve_version()
        self.assert_(self.sroot.doc1.is_version_approved())
        # copy of approved version should not be approved
        self.sroot.action_copy(['doc1'], self.REQUEST)
        self.sroot.action_paste(self.REQUEST)
        self.assert_(not self.sroot.copy_of_doc1.is_version_approved())
        # original *should* be approved
        self.assert_(self.sroot.doc1.is_version_approved())
        
    def test_copy3(self):
        # approve & publish version
        self.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc1.approve_version()
        self.assert_(self.sroot.doc1.is_version_published())
        # copy of approved version should not be approved
        self.sroot.action_copy(['doc1'], self.REQUEST)
        self.sroot.action_paste(self.REQUEST)
        self.assert_(not self.sroot.copy_of_doc1.is_version_published())
        # original *should* be published
        self.assert_(self.sroot.doc1.is_version_published())
        
    def test_copy4(self):
        # approve
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.subdoc.approve_version()
        self.assert_(self.subdoc.is_version_approved())
        # now copy the folder subdoc is in
        self.sroot.action_copy(['folder4'], self.REQUEST)
        self.sroot.action_paste(self.REQUEST)
        # the thing inside it should not be approved
        self.assert_(not self.sroot.copy_of_folder4.subdoc.is_version_approved())
        # original *should* be approved
        self.assert_(self.subdoc.is_version_approved())
        
    def test_copy5(self):
        # approve & publish
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.subdoc.approve_version()
        self.assert_(self.subdoc.is_version_published())
        # now copy the folder subdoc is in
        self.sroot.action_copy(['folder4'], self.REQUEST)
        self.sroot.action_paste(self.REQUEST)
        # the thing inside it should not be published
        self.assert_(not self.sroot.copy_of_folder4.subdoc.is_version_published())
        # original *should* be published
        self.assert_(self.subdoc.is_version_published())

    def test_copy6(self):
        # approve & publish
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.subdoc.approve_version()
        self.assert_(self.subdoc.is_version_published())
        # now copy the folder subdoc is in
        self.sroot.action_copy(['folder4'], self.REQUEST)
        # into folder5
        self.sroot.folder5.action_paste(self.REQUEST)
        # the thing inside it should not be published
        self.assert_(not self.sroot.folder5.folder4.subdoc.is_version_published())
        # original *should* be published
        self.assert_(self.subdoc.is_version_published())


    def test_copy7(self):
        # test for issue 92: pasted ghosts have unknown author
        add_helper(self.sroot.folder4, 'Ghost', 'ghost6', 'Test Ghost')
        self.sroot.folder4.ghost6.sec_update_last_author_info()
        self.assertEquals('TestUser', self.sroot.folder4.ghost6.sec_get_last_author_info().fullname())
        # copy ghost to folder 4 and check author
        # XXX maybe we should rename the user inbetween ?
        self.sroot.folder4.action_copy(['ghost6'], self.REQUEST)
        self.sroot.folder5.action_paste(self.REQUEST)
        self.assertEquals('TestUser', self.sroot.folder5.ghost6.sec_get_last_author_info().fullname())
        # move ghost to root and check author        
        self.sroot.folder4.action_cut(['ghost6'], self.REQUEST)
        self.sroot.action_paste(self.REQUEST)
        self.assertEquals('TestUser', self.sroot.ghost6.sec_get_last_author_info().fullname())
        

    def test_cut1(self):
        # try to cut object to paste it to the same folder
        self.sroot.action_cut(['doc1'], self.REQUEST)
        self.sroot.action_paste(self.REQUEST)
        self.assert_(hasattr(self.sroot, 'doc1'))

    def test_cut2(self):
        # try to cut object and paste it into another folder
        self.sroot.action_cut(['doc1'], self.REQUEST)
        self.sroot.folder4.action_paste(self.REQUEST)
        self.assert_(not hasattr(self.sroot, 'doc1'))
        self.assert_(hasattr(self.sroot.folder4, 'doc1'))

    def test_cut3(self):
        # try to cut folder and paste it into another folder
        self.sroot.action_cut(['folder4'], self.REQUEST)
        self.sroot.folder5.action_paste(self.REQUEST)
        self.assert_(not hasattr(self.sroot, 'folder4'))
        self.assert_(hasattr(self.sroot.folder5, 'folder4'))

    def test_cut4(self):
        # try to cut and paste folder to this folder again
        self.sroot.action_cut(['folder4'], self.REQUEST)
        self.sroot.action_paste(self.REQUEST)
        self.assert_(hasattr(self.sroot, 'folder4'))

    def test_cut5(self):
        # try to cut an approved content
        # should lead to an empty clipboard
        self.sroot.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.sroot.doc1.approve_version()
        self.sroot.action_cut(['doc1'], self.REQUEST)
        self.sroot.folder4.action_paste(self.REQUEST)
        self.assert_(hasattr(self.sroot.aq_explicit, 'doc1'),
                     msg='doc1 should be still in root folder')
        self.assert_(not hasattr(self.sroot.folder4.aq_explicit, 'doc1'),
                     msg='doc1 should not be pasted in folder4')

    # should add unit tests for cut-pasting approved content
    # could occur if content is approved after its put on clipboard..

    def test_cut6(self):
        # try to cut a content, approve it and paste it later on
        # (should lead to an error at paste time, for now nothing happens)
        self.sroot.action_cut(['doc1'], self.REQUEST)
        self.sroot.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.sroot.doc1.approve_version()
        self.assert_(self.sroot.doc1.is_published())
        self.sroot.folder4.action_paste(self.REQUEST)
        self.assert_(hasattr(self.sroot.aq_explicit, 'doc1'),
                     msg='doc1 should be still in root folder')
        self.assert_(not hasattr(self.sroot.folder4.aq_explicit, 'doc1'),
                     msg='doc1 should not be pasted in folder4')


    
    def test_delete1(self):
        # just delete doc1, it should work
        self.assert_(self.sroot.is_delete_allowed('doc1'))
        self.sroot.action_delete(['doc1'])
        self.assert_(not hasattr(self.sroot, 'doc1'))

    def test_delete2(self):
        # just delete folder4, it should work
        self.assert_(self.sroot.is_delete_allowed('folder4'))
        self.sroot.action_delete(['folder4'])
        self.assert_(not hasattr(self.sroot, 'folder4'))
        
    def test_delete3(self):
        # make doc1 approved
        self.doc1.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.doc1.approve_version()
        # now try to delete it (shouldn't be possible)
        self.assert_(not self.sroot.is_delete_allowed('doc1'))
        self.sroot.action_delete(['doc1'])
        # should still be there
        self.assert_(hasattr(self.sroot, 'doc1'))
        
    def test_delete4(self):
        # make doc1 approved & published
        self.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc1.approve_version()
        # now try to delete it (shouldn't be possible)
        self.assert_(not self.sroot.is_delete_allowed('doc1'))
        self.sroot.action_delete(['doc1'])
        # should still be there
        self.assert_(hasattr(self.sroot, 'doc1'))

    def test_delete5(self):
        # approve
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.subdoc.approve_version()
        self.assert_(not self.sroot.is_delete_allowed('folder4'))
        self.sroot.action_delete(['folder4'])
        # should still be there, as it contains an approved subdoc
        self.assert_(hasattr(self.sroot, 'folder4'))

    def test_delete6(self):
        # approve & published
        self.subdoc.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.subdoc.approve_version()
        self.assert_(not self.sroot.is_delete_allowed('folder4'))
        self.sroot.action_delete(['folder4'])
        # should still be there, as it contains a published subdoc
        self.assert_(hasattr(self.sroot, 'folder4'))

    def test_delete7(self):
        # delete folder without default doc
        self.folder4.action_delete(['index'])
        self.assert_(not hasattr(self.folder4.aq_explicit, 'index'))
        self.sroot.action_delete(['folder4'])
        self.assert_(not hasattr(self.sroot, 'folder4'))

    def test_rename1(self):
        self.sroot.action_rename('doc1', 'docrenamed')
        self.assert_(not hasattr(self.sroot, 'doc1'))
        self.assert_(hasattr(self.sroot, 'docrenamed'))

    def test_rename2(self):
        self.doc1.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.doc1.approve_version()
        self.sroot.action_rename('doc1', 'docrenamed')
        self.assert_(hasattr(self.sroot, 'doc1'))
        self.assert_(not hasattr(self.sroot, 'docrenamed'))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CopyTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()

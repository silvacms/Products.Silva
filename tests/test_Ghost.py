import unittest
import Zope
from Products.Silva import Interfaces
from Products.Silva.SilvaObject import SilvaObject
from DateTime import DateTime
from Products.Silva.Document import Document
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva.Ghost import Ghost, GhostVersion

def add_helper(object, typename, id, title):
    getattr(object.manage_addProduct['Silva'], 'manage_add%s' % typename)(id, title)
    return getattr(object, id)

# need to monkey patch preview and view
def preview(self):
    return render_preview(self)

def view(self):
    return render_view(self)

def render_preview(self):
    version = self.get_previewable()
    if version is None:
        return '%s no view' % self.id
    if self.meta_type == 'Silva Ghost':
        result = version.render_preview()
        if result is None:
            return 'Ghost is broken'
        else:
            return result
    else:
        return "%s %s" % (self.id, version.id)
    
def render_view(self):
    version = self.get_viewable()
    if version is None:
        return '%s no view' % self.id
    if self.meta_type == 'Silva Ghost':
        result = version.render_view()
        if result is None:
            return 'Ghost is broken'
        else:
            return result
    else:
        return "%s %s" % (self.id, version.id)

# awful HACK
def _getCopyParsedXML(self, container):
    """A hack to make copy & paste work (used by create_copy())
    """
    return ParsedXML(self.id, self.index_html())

def _getCopyGhostVersion(self, container):
    return GhostVersion(self.id, self.get_content_url())

def _verifyObjectPaste(self, ob):
    return

class GhostTestCase(unittest.TestCase):
    """Test the Ghost object.
    """
    def setUp(self):
        # monkey patch so we don't depend on service_view_registry when
        # unit testing
        self.oldpreview = SilvaObject.preview
        self.oldview = SilvaObject.view
        SilvaObject.preview = preview
        SilvaObject.view = view
        # awful HACK to support manage_clone
        ParsedXML._getCopy = _getCopyParsedXML
        Document._verifyObjectPaste = _verifyObjectPaste
        GhostVersion._getCopy = _getCopyGhostVersion
        Ghost._verifyObjectPaste = _verifyObjectPaste
        
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = self.connection.root()['Application']
        self.sroot = sroot = add_helper(self.root, 'Root', 'root', 'Root')
        self.doc1 = doc1 = add_helper(sroot, 'Document', 'doc1', 'Doc1')
        self.doc2 = doc2 = add_helper(sroot, 'Document', 'doc2', 'Doc2')
        self.doc3 = doc3 = add_helper(sroot, 'Document', 'doc3', 'Doc3')
        self.folder4 = folder4 = add_helper(sroot, 'Folder', 'folder4', 'Folder4')
        self.publication5 = publication5 = add_helper(sroot, 'Publication',
                                                      'publication5', 'Publication5')
        self.subdoc = subdoc = add_helper(folder4, 'Document', 'subdoc', 'Subdoc')
        self.subfolder = subfolder = add_helper(folder4, 'Folder', 'subfolder', 'Subfolder')
        self.subsubdoc = subsubdoc = add_helper(subfolder, 'Document', 'subsubdoc', 'Subsubdoc')
        self.subdoc2 = subdoc2 = add_helper(publication5, 'Document', 'subdoc2', 'Subdoc2')

    def tearDown(self):
        SilvaObject.preview = self.oldpreview
        SilvaObject.view = self.oldview
        
        get_transaction().abort()
        self.connection.close()

    def test_ghost(self):
        self.sroot.manage_addProduct['Silva'].manage_addGhost('ghost1',
                                                              '/root/doc1')
        ghost = getattr(self.sroot, 'ghost1')
        
        # there is no version published at all there
        self.assertEquals('doc1 no view', ghost.preview())
        self.assertEquals('ghost1 no view', ghost.view())

        # approve version of thing we point to
        self.doc1.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.doc1.approve_version()

        # since there is still no published version, preview and view return
        # None
        self.assertEquals('doc1 no view', ghost.preview())
        self.assertEquals('ghost1 no view', ghost.view())

        # this should publish doc1
        self.doc1.set_approved_version_publication_datetime(DateTime() - 1)
        
        self.assertEquals('doc1 0', ghost.preview())
        self.assertEquals('ghost1 no view', ghost.view())

        # publish ghost version
        ghost.set_unapproved_version_publication_datetime(DateTime() - 1)
        ghost.approve_version()

        self.assertEquals('doc1 0', ghost.preview())
        self.assertEquals('doc1 0', ghost.view())

        # make new version of doc1 ('1')
        self.doc1.REQUEST = None
        self.doc1.create_copy()

        # shouldn't affect what we're ghosting
        self.assertEquals('doc1 0', ghost.preview())
        self.assertEquals('doc1 0', ghost.view())

        self.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc1.approve_version()

        # now we're ghosting the version 1
        self.assertEquals('doc1 1', ghost.preview())
        self.assertEquals('doc1 1', ghost.view())

        # create new version of ghost
        ghost.REQUEST = None
        ghost.create_copy()
        ghost.get_editable().set_content_url('/root/doc2')

        self.assertEquals('doc2 no view', ghost.preview())
        self.assertEquals('doc1 1', ghost.view())

        # publish doc2
        self.doc2.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc2.approve_version()

        self.assertEquals('doc2 0', ghost.preview())
        self.assertEquals('doc1 1', ghost.view())

        # approve ghost again
        ghost.set_unapproved_version_publication_datetime(DateTime() - 1)
        ghost.approve_version()

        self.assertEquals('doc2 0', ghost.preview())
        self.assertEquals('doc2 0', ghost.view())

        # publish a ghost pointing to something that hasn't a published
        # version
        ghost.create_copy()
        ghost.get_editable().set_content_url('/root/doc3')
        ghost.set_unapproved_version_publication_datetime(DateTime() - 1)
        ghost.approve_version()
        self.assertEquals('doc3 no view', ghost.preview())
        self.assertEquals('doc3 no view', ghost.view())
        
    def test_broken_link1(self):
        # add a ghost
        self.sroot.manage_addProduct['Silva'].manage_addGhost('ghost1',
                                                              '/root/doc1')
        ghost = getattr(self.sroot, 'ghost1')
        # now delete doc1
        self.sroot.action_delete(['doc1'])
        # ghost should say 'This ghost is broken'
        self.assertEquals('Ghost is broken', ghost.preview())

        # now make ghost point to doc2, and publish ghost and doc2
        self.doc2.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc2.approve_version()
        ghost.create_copy()
        ghost.get_editable().set_content_url('/root/doc2')
        ghost.set_unapproved_version_publication_datetime(DateTime() - 1)
        ghost.approve_version()
        # now close & delete doc2
        self.doc2.close_version()
        self.sroot.action_delete(['doc2'])
        self.assertEquals('Ghost is broken', ghost.view())

    def test_ghost_title(self):
        self.sroot.manage_addProduct['Silva'].manage_addGhost('ghost1',
                                                              '/root/doc1')
        ghost = getattr(self.sroot, 'ghost1')
        # FIXME: should we be able to get title of unpublished document?
        self.assertEquals('Doc1', ghost.get_title())
        # now publish ghost
        ghost.set_unapproved_version_publication_datetime(DateTime() - 1)
        ghost.approve_version()
        # should have title of whatever we're pointing at now
        self.assertEquals('Doc1', ghost.get_title())
        # now break link
        self.sroot.action_delete(['doc1'])
        self.assertEquals('Ghost target is broken', ghost.get_title())

    # FIXME: ghost should do read access checks, test for it somehow?

    def test_ghost_points(self):
        # test that the ghost cannot point to the wrong thing;
        # only non-ghost versioned content
        self.sroot.manage_addProduct['Silva'].manage_addGhost('ghost1',
                                                              '/root/folder4')
        ghost = getattr(self.sroot, 'ghost1')
        self.assertEquals('Ghost is broken', ghost.preview())
        ghost.get_editable().set_content_url('/root/ghost1')
        self.assertEquals('Ghost is broken', ghost.preview())
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GhostTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()

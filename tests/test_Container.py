# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.38 $
import unittest
from os.path import dirname, join
import Zope
Zope.startup()
from Products.Silva.IContent import IContent
from Products.Silva.IVersionedContent import IVersionedContent
from Products.Silva.ISilvaObject import ISilvaObject
from Products.Silva.Folder import Folder
import Products.Silva.Folder
from Products.Silva.SilvaObject import SilvaObject
from Products.Silva.helpers import check_valid_id, IdCheckValues
from Testing import makerequest
from Products.ParsedXML import ParsedXML
from DateTime import DateTime
from test_SilvaObject import hack_create_user

def add_helper(object, typename, id, title, **kw):
    getattr(object.manage_addProduct['Silva'], 'manage_add%s' % typename)(id, title, **kw)
    return getattr(object, id)


def _rotten_index_helper(folder):
    """ helper for test_rotten_index """
    folder.manage_addDocument('index','DTML Document to trigger an error')

def sort_addables(a, b):
    """Sorts addables by name"""
    return cmp(a['name'], b['name'])

class ContainerBaseTestCase(unittest.TestCase):


    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        try:
            self.root = makerequest.makerequest(self.connection.root()
                                                ['Application'])
            self.REQUEST = self.root.REQUEST
            self.REQUEST['URL1'] = ''
            self.root.REQUEST['URL1'] = ''
            # make it work with SimpleMembership by creating a user. This way,
            # member object will be automatically created, so that the last
            # author username is indeed 'TestUser'
            hack_create_user(self.root)
            
            self.sroot = sroot = add_helper(self.root, 'Root', 'root', 'Root')
            self.doc1 = doc1 = add_helper(sroot, 'Document', 'doc1', 'Doc1')
            self.doc2 = doc2 = add_helper(sroot, 'Document', 'doc2', 'Doc2')
            self.doc3 = doc3 = add_helper(sroot, 'Document', 'doc3', 'Doc3')
            self.folder4 = folder4 = add_helper(sroot,
                     'Folder', 'folder4', 'Folder4')
            self.publication5 = publication5 = add_helper(sroot,
                     'Publication', 'publication5', 'Publication5')
            self.subdoc = subdoc = add_helper(folder4,
                     'Document', 'subdoc', 'Subdoc')
            self.subfolder = subfolder = add_helper(folder4,
                      'Folder', 'subfolder', 'Subfolder')
            self.subsubdoc = subsubdoc = add_helper(subfolder,
                      'Document', 'subsubdoc', 'Subsubdoc')
            self.subdoc2 = subdoc2 = add_helper(publication5,
                      'Document', 'subdoc2', 'Subdoc2')
            directory = dirname(__file__)
            test_image_filename = join(directory,'data','testimage.gif')
            test_image = open(test_image_filename, 'r')
            self.image1 = add_helper(sroot, 'Image','image1', 'Image1',
                                     file=test_image)
            test_image.close()
            test_image = open(test_image_filename, 'r')
            self.image2 = add_helper(sroot, 'Image','image2', 'Image2',
                                     file=test_image)
            test_image.close()
            # adding role for action_rename may succeed
            self.root.manage_addLocalRoles('TestUser', ['Manager'])
            get_transaction().commit(1)
        except:
            self.tearDown()
            raise          

        
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()
        
class ContainerTestCase(ContainerBaseTestCase):
    """Test the Container interface.
    """
    
    def test_get_default(self):
        doc = self.folder4.get_default()
        self.assertEquals(doc.get_title(), 'Folder4')
        self.assert_(IContent.isImplementedBy(doc),
                     'doc is not a Content object')
        self.assert_(doc.is_default(),
                     'Default document is_default gives false')

    def test_get_ordered_publishables(self):
        l = [self.doc1, self.doc2, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        l = [self.subdoc, self.subfolder]
        self.assertEquals(self.folder4.get_ordered_publishables(),
                          l)

    def test_get_nonactive_publishables(self):
        self.doc2.deactivate()
        ordered = [self.doc1, self.doc3, self.folder4, self.publication5]
        nonactive = [self.doc2]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          ordered)
        self.assertEquals(self.sroot.get_nonactive_publishables(),
                          nonactive)
        # deactivating something inactive shouldn't do anything
        self.doc2.deactivate()
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          ordered)
        self.assertEquals(self.sroot.get_nonactive_publishables(),
                          nonactive)
        self.doc2.activate()
        ordered = [self.doc1, self.doc3, self.folder4, self.publication5,
                   self.doc2]
        nonactive = []
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          ordered)
        self.assertEquals(self.sroot.get_nonactive_publishables(),
                          nonactive)
        # activating something active shouldn't do anything
        self.doc2.activate()
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          ordered)
        self.assertEquals(self.sroot.get_nonactive_publishables(),
                          nonactive)
        
    def test_get_assets(self):
        self.assertEquals(self.sroot.get_assets(), [self.image1, self.image2])
        # assets should be sorted by id
        r = self.sroot.action_rename('image2','aimage')
        self.assertEquals(self.sroot.get_assets(), [self.image2, self.image1])
        # FIXME: more tests with assets

    def test_get_tree(self):
        l = [(0, self.doc1), (0, self.doc2), (0, self.doc3),
             (0, self.folder4), (1, self.subdoc), (1, self.subfolder),
             (2, self.subfolder.subsubdoc), (0, self.publication5)]
        self.assertEquals(self.sroot.get_tree(),
                          l)
        l = [(0, self.folder4), (1, self.subfolder),
             (0, self.publication5)]
        self.assertEquals(self.sroot.get_container_tree(),
                          l)
        
    def test_get_status_tree(self):
        l = [(0, self.sroot.index), (0, self.doc1), (0, self.doc2), (0, self.doc3),
             (0, self.folder4), (1, self.folder4.index), (1, self.subdoc),
             (1, self.subfolder), (2, self.subfolder.index), (2, self.subfolder.subsubdoc),
             (0, self.sroot.publication5)]
        self.assertEquals(self.sroot.get_status_tree(),
                          l)
        
    def test_move_object_up(self):
        r = self.sroot.move_object_up('doc2')
        l = [self.doc2, self.doc1, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(r)
        r = self.sroot.move_object_up('doc2')
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(not r)

        r = self.sroot.move_object_up('folder4')
        l = [self.doc2, self.doc1, self.folder4, self.doc3, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(r)
        self.doc1.deactivate()
        self.assert_(not self.sroot.move_object_up('doc1'))

    def test_move_object_down(self):
        r = self.sroot.move_object_down('doc2')
        l = [self.doc1, self.doc3, self.doc2, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(r)
        r = self.sroot.move_object_down('publication5')
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(not r)

        r = self.sroot.move_object_down('folder4')
        l = [self.doc1, self.doc3, self.doc2, self.publication5, self.folder4]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(r)
        self.doc1.deactivate()
        self.assert_(not self.sroot.move_object_down('doc1'))

    def test_move_to_single_item_down(self):
        # move of a single item down
        r = self.sroot.move_to(['doc2'], 4)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.folder4, self.publication5, self.doc2]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
    def test_move_to_single_item_up(self):
        # move of a single item up
        r = self.sroot.move_to(['doc3'], 1)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.doc2, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)

    def test_move_to_multiple_consecutive(self):
        # move of multiple consecutive items
        r = self.sroot.move_to(['doc3', 'folder4'], 0)
        self.assert_(r)
        l = [self.doc3, self.folder4, self.doc1, self.doc2, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)

    def test_move_to_multiple_consecutive_wrong_order(self):
        r = self.sroot.move_to(['folder4', 'doc3'], 0)
        self.assert_(r)
        l = [self.doc3, self.folder4, self.doc1, self.doc2, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)

    def test_move_to_multiple_nonconsecutive(self):
        r = self.sroot.move_to(['doc1', 'publication5', 'doc3'], 4)
        self.assert_(r)
        l = [self.doc2, self.folder4, self.doc1, self.doc3, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
    
    def test_move_to_all(self):
        r = self.sroot.move_to(['doc1', 'doc2', 'doc3', 'folder4', 'publication5'], 1)
        self.assert_(r)
        l = [self.doc1, self.doc2, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        
    def test_move_to_end(self):
        r = self.sroot.move_to(['doc2'], 5)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.folder4, self.publication5, self.doc2]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        
    def test_move_to_wrong_indexes(self):
        r = self.sroot.move_to(['doc2'], 100)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.folder4, self.publication5, self.doc2]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        
    def test_move_wrong_ids(self):
        r = self.sroot.move_to(['foo'], 1)
        self.assert_(not r)
        r = self.sroot.move_to(['doc2', 'foo'], 1)
        self.assert_(not r)
        l = [self.doc1, self.doc2, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)

    def test_is_id_valid(self):
        r = self.sroot.manage_addProduct['Silva'].manage_addDocument('__this_is_wrong', 'Wrong')
        self.assert_(not hasattr(self.sroot, '__this_is_wrong'))
        r = self.sroot.manage_addProduct['Silva'].manage_addDocument('this is wrong too', 'This is wrong')
        self.assert_(not hasattr(self.sroot, 'this is wrong too'))
        r = self.sroot.manage_addProduct['Silva'].manage_addFolder('this$iswrong', 'This is wrong too')
        self.assert_(not hasattr(self.sroot, 'this$iswrong'))
        r = self.sroot.manage_addProduct['Silva'].manage_addFolder('.this__', 'Cannot be')
        self.assert_(not hasattr(self.sroot, '.this__'))
        r = self.sroot.manage_addProduct['Silva'].manage_addDocument('.foo_', 'This should not work')
        self.assert_(not hasattr(self.sroot, '.foo_'))
        # issues189/321
        for bad_id in ('service_foo', 'edit', 'manage_main', 'index_html'):
            r = self.sroot.manage_addProduct['Silva'].manage_addDocument(bad_id, 'This should not work')
            obj = getattr(self.sroot, bad_id, None)            
            self.assert_(not IVersionedContent.isImplementedBy(obj),
                         'should not have created document with id '+bad_id)
        
        # during rename
        r = self.sroot.action_rename('doc1', '_doc')
        self.assert_(hasattr(self.sroot, 'doc1'))
        self.assert_(not hasattr(self.sroot, '_doc'))


    def test_check_valid_id(self):
        self.assertEquals(check_valid_id(self.folder4, 'doc2'),
                          IdCheckValues.ID_OK)
        self.assertEquals(check_valid_id(self.folder4, self.folder4.id),
                          IdCheckValues.ID_OK)
        self.assertEquals(check_valid_id(self.folder4, 'subdoc'),
                          IdCheckValues.ID_IN_USE_CONTENT)
        self.assertEquals(check_valid_id(self.folder4, 'subdoc',
                                         allow_dup=1),
                          IdCheckValues.ID_OK)
        self.assertEquals(check_valid_id(self.folder4, 'service_foo'),
                          IdCheckValues.ID_RESERVED_PREFIX)
        self.assertEquals(check_valid_id(self.folder4, 'edit'),
                          IdCheckValues.ID_RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'edit',
                                         allow_dup=1),
                          IdCheckValues.ID_RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'manage'),
                          IdCheckValues.ID_RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'title'),
                          IdCheckValues.ID_RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'index_html'),
                          IdCheckValues.ID_RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'index_html',
                                         allow_dup=1),
                          IdCheckValues.ID_RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'get_title_or_id'),
                          IdCheckValues.ID_RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'get_title_or_id',
                                         allow_dup=1),
                          IdCheckValues.ID_RESERVED)



    def test_get_default(self):
        # add default to root
        self.sroot.manage_addProduct['Silva']
        #.manage_addDocument('index', 'Default')
        self.assertEquals(getattr(self.sroot, 'index'), self.sroot.get_default())
        # issue 47: index created by test user
        # XXX should strip the '(not in ldap)' if using LDAPUserManagement?
        self.assertEquals('TestUser',
                          self.folder4.index.sec_get_last_author_info().userid())
        self.assertEquals('TestUser',
                          self.publication5.index.sec_get_last_author_info().userid())
        # delete default object
        self.folder4.action_delete(['index'])
        self.assertEquals(None, self.folder4.get_default())


    def test_rotten_default(self):
        """ test for issue 85: if default is something odd, is_published should not create endless loop.
        actually this has been an issue if the "index" does not have a "is_published"
        and acquired it from container itself, causing the endless loop."""

        self.sroot.manage_addProduct['Silva'].manage_addFolder('folder6','Folder with broken index')
        folder = self.sroot.folder6
        folder.manage_delObjects(['index'])
        folder.manage_addDocument('index','DTML Document to trigger an error')

        self.assert_(self.sroot.folder6.get_default())
        self.assertRaises(AttributeError, self.sroot.folder6.is_published)

    def test_import_xml(self):
        xml1 = """<?xml version="1.0" ?><silva><silva_publication id="test"><title>TestPub</title><silva_document id="index"><title>TestPub</title><doc><p>Content</p></doc></silva_document></silva_publication></silva>"""

        xml2 = '<silva><silva_folder id="test2"><title>TestFolder</title><silva_demoobject id="do"><title>DemoObject</title><number>10</number><date>%s</date><info>Info</info><doc><p>Content</p></doc></silva_demoobject></silva_folder></silva>' % DateTime('2002/10/16')

        self.sroot.xml_import(xml1)

        self.assert_(hasattr(self.sroot, 'test'))
        self.assertEquals(self.sroot.test.get_title_editable(), 'TestPub')
        self.assert_(hasattr(self.sroot.test, 'index'))
        self.assertEquals(self.sroot.test.index.get_title_editable(), 'TestPub')
        self.assert_(str(self.sroot.test.index.get_editable().content.documentElement) == '<doc><p>Content</p></doc>')

        self.sroot.xml_import(xml2)

        self.assert_(hasattr(self.sroot, 'test2'))
        # XXX no title available as no index object in this import..
        #self.assertEquals(self.sroot.test2.get_title_editable(), 'TestFolder')
        self.assert_(hasattr(self.sroot.test2, 'do'))
        self.assertEquals(self.sroot.test2.do.get_title_editable(), 'DemoObject')
        self.assertEquals(str(self.sroot.test2.do.get_editable().number()), '10')
        self.assertEquals(self.sroot.test2.do.get_editable().date(), DateTime('2002/10/16'))
        self.assertEquals(self.sroot.test2.do.get_editable().info(), 'Info')
        self.assertEquals(str(self.sroot.test2.do.get_editable().content.documentElement), '<doc><p>Content</p></doc>')

class AddableTestCase(ContainerBaseTestCase):

    def setUp(self):
        ContainerBaseTestCase.setUp(self)
        # hack so we pretend we have add view for all addables
        self.sroot.service_view_registry.has_view = lambda x, y: 1
        self.original_get_silva_addables_allowed = Folder.get_silva_addables_allowed
        self.original_filtered_meta_types = Folder.filtered_meta_types
        Folder.filtered_meta_types = filtered_meta_types_hack
        
    def tearDown(self):
        ContainerBaseTestCase.tearDown(self)
        Folder.get_silva_addables_allowed = self.original_get_silva_addables_allowed
        Folder.filtered_meta_types = self.original_filtered_meta_types

    def get_meta_types(self, addables):
        return [addable['name'] for addable in addables]
    
    def test_get_silva_addables(self):
        l = ['Bar', 'Baz', 'Foo', 'Qux']
        l.sort()
        self.assertEquals(l, self.folder4.get_silva_addables_allowed())

        adbs = self.folder4.get_silva_addables()
        adbs.sort(sort_addables)
        self.assertEquals(l, self.get_meta_types(adbs))
        # modify so we explicitly allow only a few objects
        Folder.get_silva_addables_allowed = get_silva_addables_allowed_hack
        adbs = self.folder4.get_silva_addables()
        adbs.sort(sort_addables)
        self.assertEquals(['Bar', 'Foo'], self.get_meta_types(adbs))
  
    def test_silva_addables_all(self):
        l = ['Bar', 'Baz', 'Foo', 'Qux']
        l.sort()
        self.assertEquals(l, self.sroot.get_silva_addables_all())
        
    def test_silva_addables_in_publication_allowed(self):
        self.sroot.set_silva_addables_allowed_in_publication(['Foo', 'Bar'])
        l = ['Foo', 'Bar']
        l.sort()
        self.assertEquals(['Foo', 'Bar'], self.sroot.get_silva_addables_allowed())
        self.assertEquals(['Foo', 'Bar'], self.folder4.get_silva_addables_allowed())
        adbs = self.folder4.get_silva_addables()
        adbs.sort(sort_addables)
        self.assertEquals(l, self.get_meta_types(adbs))
        self.sroot.set_silva_addables_allowed_in_publication(None)
        t = ['Foo', 'Bar', 'Baz', 'Qux']
        t.sort()
        adbsa = self.folder4.get_silva_addables_allowed()
        adbsa.sort()
        self.assertEquals(t, adbsa)
        adbs = self.folder4.get_silva_addables()
        adbs.sort(sort_addables)
        self.assertEquals(t, self.get_meta_types(adbs))

    def test_silva_addables_in_publication_acquire(self):
        self.sroot.set_silva_addables_allowed_in_publication(['Foo', 'Bar'])
        l = ['Foo', 'Bar']
        l.sort()
        adbs = self.publication5.get_silva_addables()
        adbs.sort(sort_addables)
        self.assertEquals(l, self.get_meta_types(adbs))
        self.publication5.set_silva_addables_allowed_in_publication(['Baz', 'Qux'])
        self.assertEquals(0,
                          self.publication5.is_silva_addables_acquired())
        adbs = self.publication5.get_silva_addables()
        adbs.sort(sort_addables)
        self.assertEquals(['Baz', 'Qux'], self.get_meta_types(adbs))
        self.publication5.set_silva_addables_allowed_in_publication(None)
        adbs = self.publication5.get_silva_addables()
        adbs.sort(sort_addables)
        self.assertEquals(l, self.get_meta_types(adbs))
        self.assertEquals(1,
                          self.publication5.is_silva_addables_acquired())
        self.sroot.set_silva_addables_allowed_in_publication(None)
        t = ['Foo', 'Bar', 'Baz', 'Qux']
        t.sort()
        adbs = self.publication5.get_silva_addables()
        adbs.sort(sort_addables)
        self.assertEquals(t, self.get_meta_types(adbs))
        self.assertEquals(1,
                          self.sroot.is_silva_addables_acquired())
        
def get_silva_addables_hack(self):
    return ['Foo', 'Bar', 'Baz', 'Qux']

def get_silva_addables_allowed_hack(self):
    return ['Foo', 'Bar', 'Hoi']

class MySilvaObject(SilvaObject):
    meta_type = 'Minimal Silva Object'
    __implements__ = ISilvaObject
    
def filtered_meta_types_hack(self):
    return [
        {'name': 'Foo',
         'instance': MySilvaObject},
        {'name': 'Bar',
         'instance': MySilvaObject},
        {'name': 'Baz',
         'instance': MySilvaObject},
        {'name': 'Qux',
         'instance': MySilvaObject}
        ]
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContainerTestCase, 'test'))
    suite.addTest(unittest.makeSuite(AddableTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()

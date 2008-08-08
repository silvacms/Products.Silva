# Copyright (c) 2003-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $

# Python
from os.path import dirname, join
from DateTime import DateTime

# Silva
from Products.Silva.interfaces import IVersionedContent, IContent
from Products.Silva.mangle import Id

import SilvaTestCase

def _rotten_index_helper(folder):
    """ helper for test_rotten_index """
    folder.manage_addDocument('index','DTML Document to trigger an error')

def sort_addables(a, b):
    """Sorts addables by name"""
    return cmp(a['name'], b['name'])

def check_valid_id(*args, **kw):
    return Id(*args, **kw).validate()

class ContainerBaseTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self.doc1 = doc1 = self.add_document(self.root, 'doc1', 'Doc1')
        self.doc2 = doc2 = self.add_document(self.root, 'doc2', 'Doc2')
        self.doc3 = doc3 = self.add_document(self.root, 'doc3', 'Doc3')
        self.folder4 = folder4 = self.add_folder(
            self.root, 'folder4', 'Folder4', policy_name='Silva AutoTOC')
        self.publication5 = publication5 = self.add_publication(
            self.root, 'publication5', 'Publication5', policy_name='Silva AutoTOC')
        self.subdoc = subdoc = self.add_document(folder4, 'subdoc', 'Subdoc')
        self.subfolder = subfolder = self.add_folder(
            folder4, 'subfolder', 'Subfolder', policy_name='Silva AutoTOC')
        self.subsubdoc = subsubdoc = self.add_document(subfolder,
                  'subsubdoc', 'Subsubdoc')
        self.subdoc2 = subdoc2 = self.add_document(publication5,
                  'subdoc2', 'Subdoc2')
        directory = dirname(__file__)
        test_image_filename = join(directory,'data','testimage.gif')
        test_image = open(test_image_filename, 'r')
        self.image1 = self.add_image(self.root, 'image1', 'Image1',
                                 file=test_image)
        test_image.close()
        test_image = open(test_image_filename, 'r')
        self.image2 = self.add_image(self.root, 'image2', 'Image2',
                                 file=test_image)
        test_image.close()
        # adding role for action_rename may succeed
        self.setRoles(['Manager'])
        
class ContainerTestCase(ContainerBaseTestCase):
    """Test the Container interface.
    """
    
    def test_get_default(self):
        doc = self.folder4.get_default()
        self.assertEquals(doc.get_title(), 'Folder4')
        self.assert_(IContent.providedBy(doc),
                     'doc is not a Content object')
        self.assert_(doc.is_default(),
                     'Default document is_default gives false')

    def test_get_ordered_publishables(self):
        l = [self.doc1, self.doc2, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
        l = [self.subdoc, self.subfolder]
        self.assertEquals(self.folder4.get_ordered_publishables(),
                          l)
        
    def test_get_assets(self):
        self.assertEquals(self.root.get_assets(), [self.image1, self.image2])
        # assets should be sorted by id
        r = self.root.action_rename('image2','aimage')
        self.assertEquals(self.root.get_assets(), [self.image2, self.image1])
        # FIXME: more tests with assets

    def test_get_tree(self):
        l = [(0, self.doc1), (0, self.doc2), (0, self.doc3),
             (0, self.folder4), (1, self.subdoc), (1, self.subfolder),
             (2, self.subfolder.subsubdoc), (0, self.publication5)]
        self.assertEquals(self.root.get_tree(),
                          l)
        l = [(0, self.folder4), (1, self.subfolder),
             (0, self.publication5)]
        self.assertEquals(self.root.get_container_tree(),
                          l)
    def test_get_public_tree(self):
        l = [(0, self.folder4), (1, self.subfolder), (0,
            self.publication5)]
        self.assertEquals(self.root.get_public_tree(), l)
        self.assertEquals(self.root.get_public_tree(1), l)
        
        l = [(0, self.folder4), (0, self.publication5)]
        self.assertEquals(self.root.get_public_tree(0), l)

    def test_get_public_tree_all(self):
        self.subdoc2.set_unapproved_version_publication_datetime(DateTime())
        self.subdoc2.approve_version()
        
        l = [(0, self.folder4), (1, self.subfolder), 
             (0, self.publication5), (1, self.subdoc2),]
        self.assertEquals(self.root.get_public_tree_all(), l)

    def test_get_status_tree(self):
        l = [(0, self.root.index), (0, self.doc1), (0, self.doc2),
            (0, self.doc3), (0, self.folder4), (1, self.folder4.index),
            (1, self.subdoc), (1, self.subfolder), (2, self.subfolder.index),
            (2, self.subfolder.subsubdoc), (0, self.root.publication5)]
        self.assertEquals(self.root.get_status_tree(), l)
        
    def test_move_object_up(self):
        r = self.root.move_object_up('doc2')
        l = [self.doc2, self.doc1, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
        self.assert_(r)
        r = self.root.move_object_up('doc2')
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
        self.assert_(not r)

        r = self.root.move_object_up('folder4')
        l = [self.doc2, self.doc1, self.folder4, self.doc3, self.publication5]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
        self.assert_(r)

    def test_move_object_down(self):
        r = self.root.move_object_down('doc2')
        l = [self.doc1, self.doc3, self.doc2, self.folder4, self.publication5]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
        self.assert_(r)
        r = self.root.move_object_down('publication5')
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
        self.assert_(not r)

        r = self.root.move_object_down('folder4')
        l = [self.doc1, self.doc3, self.doc2, self.publication5, self.folder4]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
        self.assert_(r)

    def test_move_to_single_item_down(self):
        # move of a single item down
        r = self.root.move_to(['doc2'], 4)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.folder4, self.publication5, self.doc2]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
    def test_move_to_single_item_up(self):
        # move of a single item up
        r = self.root.move_to(['doc3'], 1)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.doc2, self.folder4, self.publication5]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)

    def test_move_to_multiple_consecutive(self):
        # move of multiple consecutive items
        r = self.root.move_to(['doc3', 'folder4'], 0)
        self.assert_(r)
        l = [self.doc3, self.folder4, self.doc1, self.doc2, self.publication5]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)

    def test_move_to_multiple_consecutive_wrong_order(self):
        r = self.root.move_to(['folder4', 'doc3'], 0)
        self.assert_(r)
        l = [self.doc3, self.folder4, self.doc1, self.doc2, self.publication5]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)

    def test_move_to_multiple_nonconsecutive(self):
        r = self.root.move_to(['doc1', 'publication5', 'doc3'], 4)
        self.assert_(r)
        l = [self.doc2, self.folder4, self.doc1, self.doc3, self.publication5]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
    
    def test_move_to_all(self):
        r = self.root.move_to(['doc1', 'doc2', 'doc3', 'folder4', 'publication5'], 1)
        self.assert_(r)
        l = [self.doc1, self.doc2, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
        
    def test_move_to_end(self):
        r = self.root.move_to(['doc2'], 5)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.folder4, self.publication5, self.doc2]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
        
    def test_move_to_wrong_indexes(self):
        r = self.root.move_to(['doc2'], 100)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.folder4, self.publication5, self.doc2]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)
        
    def test_move_wrong_ids(self):
        r = self.root.move_to(['foo'], 1)
        self.assert_(not r)
        r = self.root.move_to(['doc2', 'foo'], 1)
        self.assert_(not r)
        l = [self.doc1, self.doc2, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.root.get_ordered_publishables(),
                          l)

    def test_is_id_valid(self):
        r = self.root.manage_addProduct['SilvaDocument'].manage_addDocument('__this_is_wrong', 'Wrong')
        self.assert_(not hasattr(self.root, '__this_is_wrong'))
        r = self.root.manage_addProduct['Silva'].manage_addFolder('this$iswrong', 'This is wrong too')
        self.assert_(not hasattr(self.root, 'this$iswrong'))
        r = self.root.manage_addProduct['Silva'].manage_addFolder('.this__', 'Cannot be')
        self.assert_(not hasattr(self.root, '.this__'))
        r = self.root.manage_addProduct['SilvaDocument'].manage_addDocument('.foo_', 'This should not work')
        self.assert_(not hasattr(self.root, '.foo_'))
        # issues189/321
        for bad_id in ('service_foo', 'edit', 'manage_main', 'index_html'):
            r = self.root.manage_addProduct['SilvaDocument'].manage_addDocument(bad_id, 'This should not work')
            obj = getattr(self.root, bad_id, None)            
            self.assert_(not IVersionedContent.providedBy(obj),
                         'should not have created document with id '+bad_id)
        
        # during rename
        r = self.root.action_rename('doc1', '_doc')
        self.assert_(hasattr(self.root, 'doc1'))
        self.assert_(not hasattr(self.root, '_doc'))


    def test_check_valid_id(self):
        # XXX this test is duplicate to MangleIdTest.test_validate
        self.assertEquals(check_valid_id(self.folder4, 'doc2'),
                          Id.OK)
        self.assertEquals(check_valid_id(self.folder4, self.folder4.id),
                          Id.OK)
        self.assertEquals(check_valid_id(self.folder4, 'subdoc'),
                          Id.IN_USE_CONTENT)
        self.assertEquals(check_valid_id(self.folder4, 'subdoc',
                                         allow_dup=1),
                          Id.OK)
        self.assertEquals(check_valid_id(self.folder4, 'service_foo'),
                          Id.RESERVED_PREFIX)
        self.assertEquals(check_valid_id(self.folder4, 'edit'),
                          Id.RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'edit',
                                         allow_dup=1),
                          Id.RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'manage'),
                          Id.RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'title'),
                          Id.RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'index_html'),
                          Id.RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'index_html',
                                         allow_dup=1),
                          Id.RESERVED)
        self.assertEquals(check_valid_id(self.folder4, 'get_title_or_id'),
                          Id.RESERVED_PREFIX)
        self.assertEquals(check_valid_id(self.folder4, 'get_title_or_id',
                                         allow_dup=1),
                          Id.RESERVED_PREFIX)



    def test_get_default(self):
        # add default to root
        index = getattr(self.root, 'index', None)
        if index is None:
            self.root.manage_addProduct['Silva'].manage_addGhost('index', 'Default')
            index = self.root.index
        self.assertEquals(index, self.root.get_default())
        # issue 47: index created by test user
        # XXX should strip the '(not in ldap)' if using LDAPUserManagement?
        self.assertEquals('test_user_1_',
                          self.folder4.index.sec_get_last_author_info().userid())
        self.assertEquals('test_user_1_',
                          self.publication5.index.sec_get_last_author_info().userid())
        # delete default object
        self.folder4.action_delete(['index'])
        self.assertEquals(None, self.folder4.get_default())


    def test_rotten_default(self):
        # test for issue 85: if default is something odd,
        # "is_published" should not create endless loop.
        # actually this has been an issue if the "index" does not have a "is_published"
        # and acquired it from container itself, causing the endless loop.

        self.root.manage_addProduct['Silva'].manage_addFolder('folder6','Folder with broken index')
        folder = self.root.folder6
        folder.manage_addDocument('index','DTML Document to trigger an error')

        self.assert_(self.root.folder6.get_default())
        self.assertRaises(AttributeError, self.root.folder6.is_published)


    
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContainerTestCase, 'test'))
    return suite


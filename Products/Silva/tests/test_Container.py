# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $

# Python
from DateTime import DateTime

# Silva
from Products.Silva.mangle import Id
from Products.Silva.tests import SilvaTestCase
from Products.Silva.tests.helpers import open_test_file
from silva.core.interfaces import IContent

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
        self.doc1 = self.add_document(self.root, 'doc1', 'Doc1')
        self.doc2 = self.add_document(self.root, 'doc2', 'Doc2')
        self.doc3 = self.add_document(self.root, 'doc3', 'Doc3')
        self.folder4 = folder4 = self.add_folder(
            self.root, 'folder4', 'Folder4', policy_name='Silva AutoTOC')
        self.publication5 = publication5 = self.add_publication(
            self.root, 'publication5', 'Publication5', policy_name='Silva AutoTOC')
        self.subdoc = self.add_document(folder4, 'subdoc', 'Subdoc')
        self.subfolder = subfolder = self.add_folder(
            folder4, 'subfolder', 'Subfolder', policy_name='Silva AutoTOC')
        self.subsubdoc = self.add_document(subfolder,
                  'subsubdoc', 'Subsubdoc')
        self.subdoc2 = self.add_document(publication5,
                  'subdoc2', 'Subdoc2')
        with open_test_file('testimage.gif') as test_image:
            self.image1 = self.add_image(
                self.root, 'image1', 'Image1', file=test_image)
            self.image2 = self.add_image(
                self.root, 'image2', 'Image2', file=test_image)
        # adding role for action_rename may succeed
        self.setRoles(['Manager'])

class ContainerTestCase(ContainerBaseTestCase):
    """Test the Container interface.
    """

    def test_convert_to_folder(self):
        #create a folder to test conversion with
        cf2p_id = 'cf2p'
        cf2p = self.add_folder(self.root, cf2p_id, 'folder conversion to publicaton',
                               policy_name='Silva AutoTOC')
        #it's id should be in objectIds
        self.assert_(cf2p_id in self.root.objectIds('Silva Folder'),
                     "folder is not in objectIds('Silva Folder') and should be")
        cf2p.to_publication()
        cf2p = self.root[cf2p_id]
        #should no longer be in objectIds('Silva Folder')
        self.assert_(cf2p_id not in self.root.objectIds('Silva Folder'),
                     "folder converted to publication is still in objectIds('Silva Folder') but should not be")
        #should be in objectIds('Silva Publication')
        self.assert_(cf2p_id in self.root.objectIds('Silva Publication'),
                     "folder converted to publication is not in objectIds('Silva Publication') and should be")
        cf2p.to_folder()
        cf2p = self.root[cf2p_id]
        #should no longer be in objectIds('Silva Publication')
        self.assert_(cf2p_id not in self.root.objectIds('Silva Publication'),
                     "folder is still in objectIds('Silva Publication'), but should not be")
        #should be in objectIds('Silva Folder')
        self.assert_(cf2p_id in self.root.objectIds('Silva Folder'),
                     "folder converted to publication is not in objectIds('Silva Folder') and should be")
        self.root.manage_delObjects([cf2p_id])

    def test_get_default_2(self):
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
        self.root.action_rename('image2','aimage')
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
        factory = self.root.manage_addProduct['SilvaDocument']
        self.assertRaises(
            ValueError, factory.manage_addDocument, '__this_is_wrong', 'Wrong')
        self.assertRaises(
            ValueError,
            factory.manage_addDocument, '.foo_', 'This should not work')
        factory = self.root.manage_addProduct['Silva']
        self.assertRaises(
            ValueError,
            factory.manage_addFolder, '.this__', 'Cannot be')

        # issues189/321
        factory = self.root.manage_addProduct['SilvaDocument']
        for bad_id in ('service_foo', 'edit', 'manage_main', 'index_html'):
            self.assertRaises(
                ValueError,
                factory.manage_addDocument, bad_id, 'This should not work')

        # during rename
        self.root.action_rename('doc1', '_doc')
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


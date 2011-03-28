# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $

# Python
from DateTime import DateTime

# Silva
from Products.Silva.mangle import Id
from Products.Silva.tests import SilvaTestCase
from Products.Silva.tests.helpers import open_test_file


def check_valid_id(*args, **kw):
    return Id(*args, **kw).validate()

class ContainerTestCase(SilvaTestCase.SilvaTestCase):

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



import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContainerTestCase, 'test'))
    return suite


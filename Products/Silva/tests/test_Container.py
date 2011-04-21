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



import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContainerTestCase, 'test'))
    return suite


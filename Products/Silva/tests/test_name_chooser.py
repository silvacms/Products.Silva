
import unittest
from Products.Silva.testing import FunctionalLayer


class TestNameChooser(unittest.TestCase):

    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.factory = self.root.manage_addProduct['Silva']

    def test_create_invalid_characters(self):
        """ Invalid characters a replaced.
        """
        self.factory.manage_addMockupVersionedContent('it*em', 'Item')
        self.assertTrue('it_em' in self.root.objectIds())

    def test_create_already_exists(self):
        """ A content with the same name is present in the folder.
        """
        self.factory.manage_addMockupVersionedContent('item', 'Item')
        with self.assertRaises(ValueError):
            self.factory.manage_addMockupVersionedContent('item', 'Item')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNameChooser))
    return suite

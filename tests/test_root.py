import unittest
import Zope
from Products.XA import ViewRegistry

class RootTestCase(unittest.TestCase):
    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = self.connection.root()['Application']
        self.root.manage_addProduct['XA'].manage_addRoot(
            'test_root')
        
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

    def test_RootCreated(self):
        assert hasattr(self.root, 'test_root')
        r = self.root.test_root
        assert hasattr(r, 'service_view_registry')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RootTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()

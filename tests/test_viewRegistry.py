import unittest
import Zope
from Products.XA import ViewRegistry

class ViewRegistryTestCase(unittest.TestCase):
    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = self.connection.root()['Application']
        self.root.manage_addProduct['XA'].manage_addViewRegistry(
            'test_registry')
        
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()
        
    def test_viewRegistryCreated(self):
        # registry should be created in root
        assert self.root.test_registry.id == 'test_registry'

    def test_register(self):
        r = self.root.test_registry
        r.register('edit', 'foo', 'bar')
        self.assertEqual(r.get_view_types(), ['edit'])
        self.assertEqual(r.get_meta_types('edit'), ['foo'])

    def test_unregister(self):
        r = self.root.test_registry
        r.register('edit', 'foo', 'bar')
        r.unregister('edit', 'foo')
        self.assertEqual(r.get_meta_types('edit'), [])

    def test_get_view_types(self):
        r = self.root.test_registry
        r.register('edit', 'foo', 'bar')
        self.assertEqual(r.get_view_types(), ['edit'])

    def test_get_meta_types(self):
        r = self.root.test_registry
        r.register('edit', 'foo', 'bar')
        self.assertEqual(r.get_meta_types('edit'), ['foo'])

    def test_get_view_id(self):
        r = self.root.test_registry
        r.register('edit', 'foo', 'bar')
        self.assertEqual(r.get_view_id('edit', 'foo'), 'bar')
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ViewRegistryTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
    

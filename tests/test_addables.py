import SilvaTestCase
from Products.Silva.adapters.addables import getAddablesAdapter

class OldAddablesTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self.publication = self.add_publication(
            self.root, 
            'test_publication', 
            'Test Publication', 
            create_default=0,
            policy_name='None'
            )
        
    def test_get_addables(self):
        addables = ['Silva Image']
        self.publication.set_silva_addables_allowed_in_publication(addables)
        self.assertEquals(
            ['Silva Image', 'Silva Borken test'], 
            self.publication.get_silva_addables_allowed_in_publication()
            )

class AddablesAdapterTestCase(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        self.publication = self.add_publication(
            self.root, 
            'test_publication', 
            'Test Publication', 
            create_default=0,
            policy_name='None'
            )

    def test_root_adapter(self):
        adapter = getAddablesAdapter(self.root)
        adapter.setAddables(['Silva Publication'])
        self.assertEquals(
            ['Silva Publication'], 
            adapter.getAddables()
            )
        
    def test_publication_adapter(self):
        getAddablesAdapter(self.root).setAddables(['Silva Publication'])
        addables = ['Silva Image']
        adapter = getAddablesAdapter(self.publication)
        adapter.setAddables(addables)
        self.assertEquals(
            ['Silva Image'], 
            adapter.getAddables()
            )
        
    def test_folder_adapter(self):
        self.folder = self.add_folder(
            self.publication, 
            'test_folder', 
            'Test Folder', 
            create_default=0,
            policy_name='None'
            )
        adapter = getAddablesAdapter(self.folder)
        adapter.setAddables(['Silva Image'])
        self.assertEquals(
            ['Silva Image'], 
            adapter.getAddables()
            )
        
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(OldAddablesTestCase))
    suite.addTest(unittest.makeSuite(AddablesAdapterTestCase))
    return suite

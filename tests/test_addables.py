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
        self.publication.set_silva_addables_allowed_in_container(addables)
        self.assertEquals(
            ['Silva Image'], 
            self.publication.get_silva_addables_allowed_in_container()
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
        self.folder = self.add_folder(
            self.publication, 
            'test_folder', 
            'Test Folder', 
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
        
    def test_container_adapter(self):
        getAddablesAdapter(self.root).setAddables(['Silva Publication'])
        addables = ['Silva Folder']
        adapter = getAddablesAdapter(self.publication)
        adapter.setAddables(addables)
        self.assertEquals(
            ['Silva Folder'], 
            adapter.getAddables()
            )
        folderAdapter = getAddablesAdapter(self.folder)
        folderAdapter.setAddables(['Silva Image'])
        self.assertEquals(
            ['Silva Image']
            folderAdapter.getAddables()
            )
        
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(OldAddablesTestCase))
    suite.addTest(unittest.makeSuite(AddablesAdapterTestCase))
    return suite

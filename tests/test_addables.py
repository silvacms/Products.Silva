import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

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
            ['Silva Image'], 
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
        
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(PublicationAddablesTestCase))
        suite.addTest(unittest.makeSuite(FolderAddablesTestCase))
        return suite
    
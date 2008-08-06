import SilvaTestCase

class PartialUpgradeTestCase(SilvaTestCase.SilvaTestCase):
    """tests for partial content upgrade"""
    def afterSetUp(self):
        self.folder = self.add_folder(self.root, 'folder', 'Folder')
        self.doc = self.add_document(self.folder, 'foo', 'Foo')
        
    def test_partial_upgrade(self):
        pass
        # XXX just a single simple test here, should add more along the
        # way...

        # This step upgrade have been removed.
        #         # screw up last_author_info on the document's version
        #         if hasattr(self.doc.get_editable(), '_last_author_info'):
        #             del self.doc.get_editable()._last_author_info
        #         if hasattr(self.doc.get_editable(), '_last_author_userid'):
        #             del self.doc.get_editable()._last_author_userid

        #         # now run the upgrades and see if the props are set by them
        #         self.root.upgrade_silva_object('0.9.2', 
        #                             '/'.join(self.folder.getPhysicalPath()))

        #         self.assertEquals(self.doc.get_editable()._last_author_info, None)
        #         self.assertEquals(self.doc.get_editable()._last_author_userid, None)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PartialUpgradeTestCase))
    return suite

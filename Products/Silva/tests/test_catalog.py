# $Id$
import SilvaTestCase
from DateTime import DateTime

from silva.core.interfaces import IVersion

class CatalogTestCase(SilvaTestCase.SilvaTestCase):

    def assertStatus(self, path, statuses):
        results = self.catalog.searchResults(
            version_status=statuses, path=path)
        # should get as many entries as statuses
        self.assertEquals(len(statuses), len(results))

        # make sure the statuses are the same
        statuses.sort()
        catalog_statuses = []
        for brain in results:
            object = brain.getObject()
            self.assert_(IVersion.providedBy(object))
            catalog_statuses.append(object.version_status())
        catalog_statuses.sort()
        self.assertEquals(statuses, catalog_statuses)

    def assertPath(self, path):
        results = self.catalog.searchResults(path=path)
        for brain in results:
            if brain.getPath() == path:
                return
        self.fail()

    def assertNoPath(self, path):
        results = self.catalog.searchResults(path=path)
        for brain in results:
            if brain.getPath() == path:
                self.fail()

    def assertPristineCatalog(self, extra=0):
        # the pristine catalog has no documents, just root
        results = self.catalog.searchResults()
        # the root itself and its index document (plus its version)
        self.assertEquals(3 + extra, len(results))


class ContainerCatalogTestCase(CatalogTestCase):
    def test_folder1(self):
        self.assertNoPath('/root/sub')
        self.silva.manage_addProduct['Silva'].manage_addFolder('sub', 'Sub')
        self.assertPath('/root/sub')
        self.silva.manage_delObjects(['sub'])
        self.assertNoPath('/root/sub')

    def test_folder2(self):
        self.silva.manage_addProduct['Silva'].manage_addFolder('sub', 'Sub')
        self.silva.manage_delObjects(['sub'])
        self.assertNoPath('/root/sub')
        self.assertStatus('/root/sub/index', [])

    def test_folder3(self):
        # cut & paste
        self.add_folder(self.silva, 'sub', 'Sub',
                        policy_name='Silva Document',)
        self.add_folder(self.silva, 'sub2', 'Sub',
                        policy_name='Silva Document',)
        cb = self.silva.manage_cutObjects(['sub'])
        self.silva.sub2.manage_pasteObjects(cb)
        self.assertStatus('/root/sub2/sub/index', ['unapproved'])
        self.assertStatus('/root/sub/index', [])

class AssetCatalogTestCase(CatalogTestCase):
    def test_asset1(self):
        self.add_image(self.silva, 'test', 'Test')
        self.assertPath('/root/test')
        self.silva.manage_renameObject('test', 'test2')
        self.assertNoPath('/root/test')
        self.assertPath('/root/test2')


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContainerCatalogTestCase))
    suite.addTest(unittest.makeSuite(AssetCatalogTestCase))
    return suite

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

class VersionCatalogTestCase(CatalogTestCase):

    def afterSetUp(self):
        self.add_document(self.silva, 'alpha', 'Alpha')
        self.alpha = self.silva.alpha

    def test_pristine(self):
        self.silva.manage_delObjects(['alpha'])
        self.assertPristineCatalog()

    def test_unapproved(self):
        self.assertStatus('/root/alpha', ['unapproved'])

    def test_approved(self):
        # set publication time into the future, so should be approved
        dt = DateTime() + 1
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.assertStatus('/root/alpha', ['approved'])

    def test_public(self):
        # set publication time into the past, so should go public right away
        dt = DateTime() - 1
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.assertStatus('/root/alpha', ['public'])

    def test_closed(self):
        dt = DateTime() - 1
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.alpha.close_version()
        # close unindex the version, but the versioned is kept in the catalog
        self.assertPristineCatalog(extra=1)

    def test_new(self):
        dt = DateTime() - 1
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.alpha.create_copy()
        self.assertStatus('/root/alpha', ['unapproved', 'public'])

    def test_new_approved(self):
        dt = DateTime() - 1
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.alpha.create_copy()
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.assertStatus('/root/alpha', ['public'])

    def test_rename(self):
        self.silva.manage_renameObject('alpha', 'beta')
        self.assertStatus('/root/alpha', [])
        self.assertStatus('/root/beta', ['unapproved'])

    def test_copy(self):
        cb = self.silva.manage_copyObjects(['alpha'])
        self.silva.manage_pasteObjects(cb)
        self.assert_(hasattr(self.silva, 'copy_of_alpha'))
        self.assertStatus('/root/alpha', ['unapproved'])
        self.assertStatus('/root/copy_of_alpha', ['unapproved'])

    def test_cut(self):
        self.silva.manage_addProduct['Silva'].manage_addFolder('sub', 'Sub')
        cb = self.silva.manage_cutObjects(['alpha'])
        self.silva.sub.manage_pasteObjects(cb)
        self.assertStatus('/root/alpha', [])
        self.assertStatus('/root/sub/alpha', ['unapproved'])


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

class FulltextIndexTestCase(CatalogTestCase):
    def afterSetUp(self):
        self.add_document(self.silva, 'mydoc', 'My Document')
        self.document = self.silva.mydoc
        self.editable = self.document.get_editable()

    def test_markup_not_in_fulltext_index(self):
        # For https://infrae.com/issue/silva/issue1642

        document = self.document
        editable = self.editable
        editable.content.manage_edit('''<foo> Hello world!
            <source id="">
            <parameter type="string" key="hidden_text">verboten</parameter>
            </source></foo>''')
        # We need to do this so that document.fulltext() actually
        # returns content:
        document._unapproved_version = ('0', DateTime(), None)
        document.approve_version()

        # 'Hello world!' should be found using the fulltext search
        res = self.catalog(fulltext='Hello world!')
        self.assertEquals(len(res), 1)
        self.assertEquals(res[0].getPath(), '/root/mydoc/0')

        # But not <foo>, which isn't really content
        self.assertEquals(len(self.catalog(fulltext='foo')), 0)

        # Also not 'verboten', because external sources are removed
        # from the fulltext.
        self.assertEquals(len(self.catalog(fulltext='verboten')), 0)


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersionCatalogTestCase))
    suite.addTest(unittest.makeSuite(ContainerCatalogTestCase))
    suite.addTest(unittest.makeSuite(AssetCatalogTestCase))
    suite.addTest(unittest.makeSuite(FulltextIndexTestCase))
    return suite

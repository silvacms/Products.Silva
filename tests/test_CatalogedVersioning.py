# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from DateTime import DateTime
import time

import SilvaTestCase

class CatalogedVersioningTestCase(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.add_document(self.root, 'test','Test')
        self.service_catalog = self.root.service_catalog
        self.test = self.root.test

    def _objects_to_paths(self, objects):
        result = []
        for object in objects:
            result.append('/'.join(object.getPhysicalPath()))
        return result

    def assertInCatalog(self, objects, **kw):
        self.assertInCatalogByPath(self._objects_to_paths(objects), **kw)

    def assertNotInCatalog(self, objects, **kw):
        self.assertNotInCatalogByPath(self._objects_to_paths(objects), **kw)

    def assertInCatalogByPath(self, search_paths, **kw):
        result = self.service_catalog.searchResults(**kw)
        paths = [entry.getPath() for entry in result]
        for search_path in search_paths:
            if search_path not in paths:
                self.fail('Could not find object %s in catalog.' % search_path)

    def assertNotInCatalogByPath(self, search_paths, **kw):
        result = self.service_catalog.searchResults(**kw)
        paths = [entry.getPath() for entry in result]
        for search_path in search_paths:
            if search_path in paths:
                self.fail('Object %s should not be found in catalog.' % search_path)

    def assertCatalogEmptyResult(self, **kw):
        result = self.service_catalog.searchResults(**kw)
        # only result that should exist is root and maybe its index document
        sd_installed = self.root.service_extensions.is_installed(
            'SilvaDocument')
        expeceted_items = 1
        if sd_installed:
            expeceted_items = 3
        self.assertEquals(len(result), expeceted_items,
            'Catalog results where none expected.')

    def test_add(self):
        version = self.test.get_editable()
        self.assertInCatalog([version])

# this test cannot work anymore as we moved from DemoObject to
# Document. We need to figure out what else to do
##     def test_setData(self):
##         version = self.test.get_editable()
##         self.assertNotInCatalog([version], info='info')
##         version.set_demo_data(
##             info="info", number=1, date=DateTime(2002, 10, 10))
##         self.assertInCatalog([version], info='info')
##         version.set_demo_data(
##             info="info2", number=2, date=DateTime(2002, 10, 10))
##         self.assertInCatalog([version], info='info2')
##         self.assertNotInCatalog([version], info='info')

    def test_workflow(self):
        version = self.test.get_editable()
        self.assertEquals('unapproved', version.version_status())
        self.assertInCatalog([version], version_status='unapproved')
        now = DateTime()
        self.test.set_unapproved_version_publication_datetime(now + 1)
        self.test.approve_version()
        self.assertEquals('approved', version.version_status())
        self.assertInCatalog([version], version_status='approved')
        self.test.set_approved_version_publication_datetime(now - 1)
        self.assertEquals('public', version.version_status())
        self.assertInCatalog([version], version_status='public')
        self.test.close_version()
        self.assertEquals('last_closed', version.version_status())
        self.test.create_copy()
        new_version = self.test.get_editable()
        self.assertInCatalog([new_version], version_status='unapproved')
        self.test.set_unapproved_version_publication_datetime(now - 1)
        self.test.approve_version()
        self.assertInCatalog([new_version], version_status='public')
        self.test.close_version()
        self.assertEquals('last_closed', new_version.version_status())
        self.assertEquals('closed', version.version_status())
        self.assertNotInCatalog([version], version_status='closed')

    def test_periodic_workflow_update(self):
        version = self.test.get_editable()
        now = DateTime()
        # There's probably a better way: I set the publication time to
        # approx. 5 seconds from now...
        self.test.set_unapproved_version_publication_datetime(now + 0.00005)
        # and the expiration to about 10 seconds from now...
        self.test.set_unapproved_version_expiration_datetime(now + 0.00010)
        self.test.approve_version()
        self.assertEquals(1, not not version.is_version_approved())
        self.assertEquals(0, not not version.is_version_published())
        # ..after 5 seconds the version should be published.
        time.sleep(5)
        self.root.status_update()
        self.assertEquals(0, not not version.is_version_approved())
        self.assertEquals(1, not not version.is_version_published())
        # ..after 10 seconds the version should be closed again.
        time.sleep(5)
        self.root.status_update()
        self.assertEquals(0, not not version.is_version_approved())
        self.assertEquals(0, not not version.is_version_published())
        self.assertEquals(version.id, self.test.get_last_closed_version())
        self.assertNotInCatalog([version], version_status='approved')
        self.assertNotInCatalog([version], version_status='public')

    def test_move(self):
        version = self.test.get_editable()
        self.assertInCatalog([self.test.get_editable()])
        self.root.action_rename('test', 'test2')
        test2 = self.root.test2
        self.assertNotInCatalogByPath(['/root/test/0'])
        self.assertInCatalog([test2.get_editable()])

    def test_remove(self):
        self.root.action_delete(['test'])
        self.assertNotInCatalogByPath(['/root/test/0'])
        self.assertCatalogEmptyResult()


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CatalogedVersioningTestCase))
    return suite

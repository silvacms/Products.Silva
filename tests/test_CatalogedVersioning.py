# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.6 $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase

from Products.Silva.interfaces import IContent
from Products.Silva.interfaces import ISilvaObject
from Products.Silva.Folder import Folder
from Products.Silva.SilvaObject import SilvaObject
from Products.ParsedXML import ParsedXML
from DateTime import DateTime

from Products.Silva.Root import Root

from Products.SilvaDocument.Document import Document, DocumentVersion

# XXX ugh would really like to avoid this..
Document.cb_isMoveable = lambda self: 1

def _verifyObjectPaste(self, ob):
    return

class CatalogedVersioningTestCase(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.root.manage_addProduct['SilvaDocument'].manage_addDocument(
            'test', 'Test')
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
        # only result that should exist is root
        if len(result) != 1:
            self.fail('Catalog results where none expected.')
            
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
        self.assertInCatalog([version], version_status='last_closed')
        self.test.create_copy()
        new_version = self.test.get_editable()
        self.assertInCatalog([version], version_status='last_closed')
        self.assertInCatalog([new_version], version_status='unapproved')
        self.test.set_unapproved_version_publication_datetime(now - 1)
        self.test.approve_version()
        self.assertInCatalog([new_version], version_status='approved')
        self.test.close_version()

        self.assertEquals('last_closed', new_version.version_status())
        self.assertEquals('closed', version.version_status())
        self.assertInCatalog([new_version], version_status='last_closed')
        self.assertInCatalog([version], version_status='closed')     

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
        

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(CatalogedVersioningTestCase))
        return suite


if __name__ == '__main__':
    main()

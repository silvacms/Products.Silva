# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
import unittest
import Zope
from Products.Silva.IContent import IContent
from Products.Silva.ISilvaObject import ISilvaObject
from Products.Silva.Folder import Folder
from Products.Silva.SilvaObject import SilvaObject
from Testing import makerequest
from Products.ParsedXML import ParsedXML
from DateTime import DateTime

from Products.Silva.CatalogedDemoObject import CatalogedDemoObject, CatalogedDemoObjectVersion
from Products.Silva.Root import Root

def _getCopy(self, container):
    """A hack to make copy & paste work (used by create_copy())
    """
    version = CatalogedDemoObjectVersion('test', 'test')
    version.set_demo_data(self.info(), self.number(), self.date())
    return version

def _verifyObjectPaste(self, ob):
    return

class CatalogedVersioningTestCase(unittest.TestCase):
    def setUp(self):
        # awful HACK to support manage_clone
        CatalogedDemoObjectVersion._getCopy = _getCopy
        CatalogedDemoObject._verifyObjectPaste = _verifyObjectPaste
        Root._verifyObjectPaste = _verifyObjectPaste
        
        get_transaction().begin()
        self.connection = Zope.DB.open()
        #self.root = Zope.app()
        self.root = self.connection.root()['Application']
        self.root.manage_addProduct['Silva'].manage_addRoot(
            'root', 'Root')
        self.sroot = getattr(self.root, 'root')
        self.sroot.manage_addProduct['ZCatalog'].manage_addZCatalog(
            'service_catalog', 'catalog')
        catalog = self.service_catalog = self.sroot.service_catalog
        indexes = [
            ('sources', 'KeywordIndex'),
            ('creation_datetime', 'FieldIndex'),
            ('get_approved_version_publication_datetime', 'FieldIndex'),
            ('get_next_version_publication_datetime', 'FieldIndex'),
            ('get_public_version_publication_datetime', 'FieldIndex'),
            ('get_title', 'FieldIndex'),
            ('id', 'FieldIndex'),
            ('is_approved', 'FieldIndex'),
            ('is_published', 'FieldIndex'),
            ('is_version_approved', 'FieldIndex'),
            ('is_version_published', 'FieldIndex'),
            ('meta_type', 'FieldIndex'),
            ('path', 'PathIndex'),
            ('subjects', 'KeywordIndex'),
            ('target_audiences', 'KeywordIndex'),

            # special stuff only for CatalogedDemoObject
            ('info', 'FieldIndex'),
            ('number', 'FieldIndex'),
            ('date', 'FieldIndex'),
            ]
        
        columns = [
            'creation_datetime',
            'get_next_version_expiration_datetime',
            'get_next_version_publication_datetime',
            'get_next_version_status',
            'get_public_version_expiration_datetime',
            'get_public_version_publication_datetime',
            'get_public_version_status',
            'get_title',
            'id',
            'meta_type',
            'object_status',
            'sec_get_last_author_info',
            'subjects',
            'target_audiences',
            ]

        existing_columns = catalog.schema()
        existing_indexes = catalog.indexes()
        
        for column_name in columns:
            if column_name in existing_columns:
                continue
            catalog.addColumn(column_name)

        for field_name, field_type in indexes:
            if field_name in existing_indexes:
                continue
            catalog.addIndex(field_name, field_type)

        self.sroot.manage_addProduct['Silva'].manage_addCatalogedDemoObject(
            'test', 'Test')
        self.test = getattr(self.sroot, 'test')
    
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

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
        if len(result) != 0:
            self.fail('Catalog results where none expected.')
            
    def test_add(self):
        version = self.test.get_editable()
        self.assertInCatalog([version])

    def test_setData(self):
        version = self.test.get_editable()
        self.assertNotInCatalog([version], info='info')
        version.set_demo_data(
            info="info", number=1, date=DateTime(2002, 10, 10))
        self.assertInCatalog([version], info='info')
        version.set_demo_data(
            info="info2", number=2, date=DateTime(2002, 10, 10))
        self.assertInCatalog([version], info='info2')
        self.assertNotInCatalog([version], info='info')

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
        self.test.REQUEST = None

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
        self.sroot.action_rename('test', 'test2')
        test2 = self.sroot.test2
        self.assertNotInCatalogByPath(['/root/test/0'])
        self.assertInCatalog([test2.get_editable()])

    def test_remove(self):
        self.sroot.action_delete(['test'])
        self.assertNotInCatalogByPath(['/root/test/0'])
        self.assertCatalogEmptyResult()
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CatalogedVersioningTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()

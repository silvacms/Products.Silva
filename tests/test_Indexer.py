# Copyright (c) 2003-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $
import SilvaTestCase
from DateTime import DateTime

from Products.Silva import Ghost

class IndexerTestCase(SilvaTestCase.SilvaTestCase):
                                                                                
    def afterSetUp(self):
        self.pub = pub = self.add_folder(
            self.root, 'pub', 'Publication')
        
        self.toghost  = toghost = self.add_document(
            self.root, 'toghost', 'To be Haunted')
        self.gamma  = gamma = self.add_document(self.pub, 'gamma', 'Gamma')
        self.alpha = alpha = self.add_document(self.pub, 'alpha', 'Alpha')
        self.Alpha = Alpha = self.add_document(self.pub, 'Alpha', 'Alpha Capital A')
        self.beta = beta = self.add_document(self.pub, 'beta', 'Beta')
        self.Beta = Beta = self.add_document(self.pub, 'Beta', 'Beta Capital B')
        self.kappa = kappa = self.add_document(self.pub, 'kappa', 'Kappa')
        self.ghost = ghost = self.add_ghost(
            self.pub, 'ghost', '/'.join(toghost.getPhysicalPath()))

        self.foldertoghost = self.add_folder(
            self.root, 'foldertoghost', 'Folder to Ghost')
        self.foo = foo = self.add_document(self.foldertoghost, 'index', 'Index')
        self.bar = bar = self.add_document(self.foldertoghost, 'bar', 'Barrr')
        self.baz = baz = self.add_document(self.foldertoghost, 'baz', 'Bazzz')
        self.ghostfolder = ghostfolder = Ghost.ghostFactory(
            self.pub, 'ghostfolder', self.foldertoghost)
        self.ghostfolder.haunt()

        self.broken_ghost = broken_ghost = self.add_ghost(
            self.pub, 'broken_ghost', '/this/object/does/not/exist')

        # add a folder with an indexable index document
        self.subfolder = subfolder =  self.add_folder(
            self.pub, 'folder_with_index_doc', 
            'Folder with indexable index document',
            policy_name='Silva Document')

        # also add a folder with a not indexable index document
        self.subfolder_autotoc = subfolder_autotoc = self.add_folder(
            subfolder, 'folder_with_autotoc', 
            'Folder with AutoTOC index document',
            policy_name='Silva AutoTOC')

        getattr(subfolder.index, '0').content.manage_edit(
            '<doc>'
            '<p><index name="subfolder" /></p>'
            '</doc>')
        getattr(toghost, '0').content.manage_edit(
            '<doc>'
            '<p><index name="ghost" /></p>'
            '</doc>')
        getattr(gamma, '0').content.manage_edit(
            '<doc>'
            '<p>Foo bar <index name="a" /></p>'
            '<p>Baz <index name="b" /></p>'
            '</doc>')
        getattr(alpha, '0').content.manage_edit(
            '<doc>'
            '<p>Hey <index name="a" /></p>'
            '</doc>')
        getattr(Alpha, '0').content.manage_edit(
            '<doc>'
            '<p>Hey <index name="A" /></p>'
            '</doc>')
        getattr(beta, '0').content.manage_edit(
            '<doc>'
            '<p>Hello <index name="b" /></p>'
            '</doc>')
        getattr(Beta, '0').content.manage_edit(
            '<doc>'
            '<p>Hello <index name="b" /></p>'
            '</doc>')
        getattr(kappa, '0').content.manage_edit(
            '<doc>'
            '<p>Dag <index name="c" /></p>'
            '</doc>')
        getattr(foo, '0').content.manage_edit(
            '<doc>'
            '<p>Dag <index name="f" /></p>'
            '</doc>')
        getattr(bar, '0').content.manage_edit(
            '<doc>'
            '<p>Dag <index name="g" /></p>'
            '</doc>')
        getattr(baz, '0').content.manage_edit(
            '<doc>'
            '<p>Dag <index name="h" /></p>'
            '</doc>')

        # publish documents
        for doc in [gamma, alpha, Alpha, beta, Beta, kappa, toghost, ghost,
                    broken_ghost, subfolder.index, foo, bar, baz]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

        # create one unpublished document that should never show up in the
        # index
        self.omega = omega = self.add_document(self.root, 'omega', 'Omega')

        # create a new version of a document that should not be picked up by the
        # indexer
        gamma.create_copy()
        getattr(gamma, '1').content.manage_edit(
            '<doc>'
            '<p>hello hello <index name="d" /></p>'
            '</doc>')

        # close a version of a document - should also not be picked up by the
        # indexer
        self.Beta.close_version()

        # now create the indexer itself
        self.root.pub.manage_addProduct['Silva'].manage_addIndexer(
            'indexer', 'Title')
        self.indexer = self.pub.indexer
        self.indexer.update()
        
    def test_getIndexNames(self):
        self.assertEquals(
            ['A', 'a', 'b', 'c', 'f', 'g', 'ghost', 'h', 'subfolder'], 
            self.indexer.getIndexNames())

    def test_getIndexEntry(self):
        expected = [('Alpha', ('', 'root', 'pub', 'alpha',)),
                    ('Gamma', ('', 'root', 'pub', 'gamma',)),]
        self.assertEquals(expected, self.indexer.getIndexEntry('a'))
    
    def test_getAllIndexEntries(self):
        expected = {}
        expected['a'] = [('Alpha', ('', 'root', 'pub', 'alpha',)),
                        ('Gamma', ('', 'root', 'pub', 'gamma',)),]
        expected['A'] = [(u'Alpha Capital A', ('', 'root', 'pub', 'Alpha')),]
        expected['b'] = [(u'Beta', ('', 'root', 'pub', 'beta')), 
                        (u'Gamma', ('', 'root', 'pub', 'gamma'))]
        expected['c'] = [(u'Kappa', ('', 'root', 'pub', 'kappa')),]
        expected['f'] = [(u'Folder to Ghost', ('', 'root', 'pub', 'ghostfolder')),]
        expected['g'] = [(u'Barrr', ('', 'root', 'pub', 'ghostfolder', 'bar')),]
        
        expected['ghost'] = [(u'To be Haunted', ('', 'root', 'pub', 'ghost')),]
        
        expected['h'] = [(u'Bazzz', ('', 'root', 'pub', 'ghostfolder', 'baz')),]

        expected['subfolder'] = [(u'Folder with indexable index document', 
                                 ('', 'root', 'pub', 'folder_with_index_doc')),]
 
        result =  self.indexer.getIndexNames()
        self.assertEquals(len(expected), len(result))
        for indexName in result:
            self.assertEquals(expected[indexName],
                self.indexer.getIndexEntry(indexName))
    
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IndexerTestCase, 'test'))
    return suite

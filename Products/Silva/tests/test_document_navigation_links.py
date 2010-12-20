# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $
import SilvaTestCase

from DateTime import DateTime

class ContainerTestCase(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        
        self.u = u = self.add_document(self.root, 'u', 'Document U')
        
        self.root.manage_addProduct['Silva'].manage_addPublication('a', 'A')
        self.a = self.root.a
        
        self.v = self.add_folder(
            self.root,
            'v',
            'Folder V') 
        self.indexv = indexv = self.add_document(self.v, 'indexv', 'Document W')
            
        self.w = w = self.add_document(self.root, 'w', 'Document W')
        self.x = x = self.add_document(self.a, 'x', 'Document X')
        self.y = y = self.add_document(self.a, 'y', 'Document Y')

        # 1st subtree
        self.b = self.add_folder(
            self.a,
            'b',
            'B')

        self.c = self.add_folder(
            self.b,
            'c', 
            'C')

        self.d = d = self.add_document(self.c, 'd', 'Document D')
        self.e = e = self.add_document(self.c, 'e', 'Document E')
        self.f = f = self.add_document(self.c, 'f', 'Document F')

        self.g = self.add_folder(
            self.b,
            'g',
            'G')
        self.i1 = i1 = self.add_document(self.g, 'index',
            'IndexDoc')

        # 2nd subtree
        self.h = self.add_folder(
            self.a, 
            'h', 
            'Folder H')

        self.i = i = self.add_document(self.h, 'i', 'Document I')
        
        self.j = self.add_folder(
            self.h, 
            'j', 
            'Folder J')
        self.k = k = self.add_document(self.j, 'k', 'Document K')
        self.l = l = self.add_document(self.j, 'l', 'Document L')
    

        # 3rd subtree
        self.m = self.add_folder(
            self.a,
            'm',
            'Folder M')
        
        self.n = self.add_folder(
            self.m,
            'n',
            'Folder N')
            
        self.o = self.add_folder(
            self.n,
            'o',
            'Subfolder O')
        self.i2 = i2 = self.add_document(self.o, 'index', 'Document I')
        self.p = p = self.add_document(self.n, 'p', 'Document P')
        
        # document heap
        self.q = q = self.add_document(self.root, 'q', 'Document Q')
        self.r = r = self.add_document(self.root, 'r', 'Document R')
        self.s = s = self.add_document(self.root, 's', 'Document S')
        self.t = t = self.add_document(self.a, 't', 'Document T')
        
        for doc in [d,e,f,i,k,l,p,i1,i2,q,r,s,t,u,w,indexv,x,y]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()
            
    def test_get_real_container(self):
        # folder
        container = self.m.get_real_container()
        self.assertEquals(self.a, container)

        # publication
        container = self.a.get_real_container()
        self.assertEquals(self.root, container)

        # first document in a publication
        container = self.t.get_real_container()
        self.assertEquals(self.a, container)

        # subfolder
        container = self.n.get_real_container()
        self.assertEquals(self.m, container)
        
        # document
        container = self.r.get_real_container()
        self.assertEquals(self.root, container)

    def test_get_document_navigation_links(self):
        links = self.a.get_document_navigation_links()
        self.assertEquals(self.v, links['next'])
        self.assertEquals(self.u, links['prev'])
        self.assertEquals(self.u, links['first'])
        self.assertEquals(self.s, links['last'])


class SimpleTestCase(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        # document heap
        self.a = a = self.add_document(self.root, 'a', 'Document A')
        self.b = b = self.add_document(self.root, 'b', 'Document B')
        self.c = c = self.add_document(self.root, 'c', 'Document C')
        self.d = d = self.add_document(self.root, 'd', 'Document D')
        self.e = e = self.add_document(self.root, 'e', 'Document E')
        self.f = f = self.add_document(self.root, 'f', 'Document F')
        
        # publish documents
        for doc in [a,b,c,d,e,f]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

    def test_get_document_navigation_links(self):
        # test when viewing root, with an index
        links = self.root.get_document_navigation_links()
        self.assertEquals({}, links)
        
        # test when viewing doc e, which is the last
        links = self.root.a.get_document_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.b, links['next'])
        self.assertEquals(self.f, links['last'])
        self.assertEquals(4, len(links))
        
        # test when viewing doc d, which is the middle
        links = self.root.d.get_document_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.a, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.c, links['prev'])
        self.assertEquals(self.e, links['next'])
        self.assertEquals(self.f, links['last'])
        self.assertEquals(6, len(links))
        
        # test when viewing doc f, which is the last document
        links = self.root.f.get_document_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.a, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.e, links['prev'])
        self.assertEquals(4, len(links))

        # test when viewing at the second doc (b)
        links = self.root.b.get_document_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.a, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.a, links['prev'])
        self.assertEquals(self.c, links['next'])
        self.assertEquals(self.f, links['last'])
        self.assertEquals(6, len(links))
        
        # test when viewing at the second doc (e)
        links = self.root.e.get_document_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.a, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.d, links['prev'])
        self.assertEquals(self.f, links['next'])
        self.assertEquals(self.f, links['last'])
        self.assertEquals(6, len(links))
    
        
class SubFolderIndexerTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self.folder = self.add_folder(
            self.root,
            'folder',
            'Folder with an Indexer',
            policy_name='Silva AutoTOC')
        self.folder2 = self.add_folder(
            self.root, 
            'folder2',
            'Folder 2')

        self.folder3 = self.add_folder(
            self.root,
            'folder3',
            'Folder 3')
        self.subfolder = self.add_folder(
            self.folder, 
            'subfolder',
            'Subfolder')

        self.a = a = self.add_document(self.folder, 'a', 'Document A')
        self.b = b = self.add_document(self.folder, 'b', 'Document B')
        self.c = c = self.add_document(self.root, 'c', 'Document C')
        self.root.manage_addProduct['Silva'].manage_addIndexer('foobar',
        'Title')
        self.root.folder.subfolder.manage_addProduct['Silva']\
            .manage_addPublication('publication', 'MyPublication')
        self.root.folder.subfolder.publication.manage_addProduct['Silva']\
            .manage_addIndexer('newindexer', 'Title')

        for doc in [a, b, c]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            doc.approve_version()

    def test_get_document_navigation_links(self):
        # test folder 3 with AutoTOC and unapproved document
        links = self.root.folder.get_document_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.c, links['next'])
        self.assertEquals(self.c, links['last'])
        self.assertEquals(4, len(links))

class AutoTocTestCase(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        self.a = a = self.add_document(self.root, 'a', 'Index')
        self.b = b = self.add_document(self.root, 'b', 'Document B')
        
        for doc in [a, b]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            doc.approve_version()
        
        self.root.manage_addProduct['Silva'].manage_addAutoTOC('foobar',
        'Title')
        self.root.manage_addProduct['Silva'].manage_addAutoTOC('dummy',
        'Title')
        self.root.manage_addProduct['Silva'].manage_addAutoTOC('asdf',
        'Title')
        self.dummy = self.root.dummy
        self.asdf = self.root.asdf

    def test_get_document_navigation_links(self):
        links = self.root.a.get_document_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.b, links['next'])
        self.assertEquals(self.b, links['last'])
        self.assertEquals(4, len(links))

    def test_get_document_navigation_links_2(self):
        links = self.root.index.get_document_navigation_links()
        self.assertEquals({}, links)

class AutoTocDepthTestCase(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        # This is the autotoc that we test against:
        self.root.manage_addProduct['Silva'].manage_addAutoTOC(
            'autotoc', 'Title')

        self.levels = (1,2,3)
        # Let's create a couple of nested folders to check the depth
        # feature:
        parent = self.root
        for level in self.levels + (4,5):
            folder = self.add_folder(
                parent,
                'folder%s' % level,
                'Folder %s' % level)
            setattr(self, 'folder%s' % level, folder)
            doc = self.add_document(folder, 'index', 'Index Document')
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            doc.approve_version()
            parent = folder

    def get_anchor_for(self, name):
        obj = getattr(self, name)
        return '<a href="%s">' % obj.absolute_url()

    def test_autotoc_infinite_depth(self):
        # Without any restrictions, the toc should give us all levels:
        html = self.root.autotoc.restrictedTraverse('content.html')()
        for level in self.levels:
            self.assert_(self.get_anchor_for('folder%s' % level) in html)

    def test_autotoc_all_depths(self):
        for level in self.levels:
            self.root.autotoc.set_toc_depth(level)
            html = self.root.autotoc.restrictedTraverse('content.html')()
            # Check that all levels that should be there, are there
            for l in range(1, level+2):
                self.assert_(self.get_anchor_for('folder%s' % level) in html)

            # and that the next level is *not* in there
            self.assert_(self.get_anchor_for('folder%s' % (l+1)) not in html)

class MartijnTestCase(SilvaTestCase.SilvaTestCase):
                                                                                
    def afterSetUp(self):
        self.secundus = self.add_document(self.root, 'secundus',
            'Secundus')
        self.tertius = self.add_document(self.root, 'tertius', 
            'Tertius')

        self.folder_one = self.add_folder(
            self.root, 
            'folder_1',
            'Folder 1')
        
        self.tertius.set_unapproved_version_publication_datetime(DateTime()
        - 1)
        self.tertius.approve_version()

    def test_get_document_navigation_links(self):
        # test martijn situation
        links = self.root.get_document_navigation_links()
        self.assertEquals({}, links)

        links = self.root.index.get_document_navigation_links()
        self.assertEquals({}, links)
       
        links = self.root.tertius.get_document_navigation_links()
        self.assertEquals('..', links['up'])
        self.assertEquals(self.root, links['top'])
        self.assertEquals(2, len(links))

class MartijnSecondTestCase(SilvaTestCase.SilvaTestCase):
                                                                                
    def afterSetUp(self):
        self.secundus = self.add_document(self.root, 'secundus',
            'Secundus')
        self.tertius = self.add_document(self.root, 'tertius', 
            'Tertius')

        self.folder_one = self.add_folder(
            self.root, 
            'folder_1',
            'Folder 1',)
        
        self.secundus.set_unapproved_version_publication_datetime(DateTime()
        - 1)
        self.secundus.approve_version()
        self.tertius.set_unapproved_version_publication_datetime(DateTime()
        - 1)
        self.tertius.approve_version()

    def test_get_document_navigation_links(self):
        # test martijn situation
        links = self.root.get_document_navigation_links()
        self.assertEquals({}, links)
    
        links = self.root.tertius.get_document_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.secundus, links['prev'])
        self.assertEquals(self.secundus, links['first'])
        self.assertEquals(4, len(links))

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContainerTestCase))
    suite.addTest(unittest.makeSuite(SimpleTestCase))
    suite.addTest(unittest.makeSuite(SubFolderIndexerTestCase))
    suite.addTest(unittest.makeSuite(AutoTocTestCase))
    suite.addTest(unittest.makeSuite(AutoTocDepthTestCase))
    suite.addTest(unittest.makeSuite(MartijnTestCase))
    suite.addTest(unittest.makeSuite(MartijnSecondTestCase))
    return suite

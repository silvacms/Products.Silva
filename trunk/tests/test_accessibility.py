# Copyright (c) 2003-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $
import SilvaTestCase

from DateTime import DateTime

class SimpleTreeTestCase(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        
        self.root.manage_addProduct['Silva'].manage_addPublication('a', 'A')
        self.a = self.root.a
        
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
        
        for doc in [d,e,f,i,k,l,p, i1,i2]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()
    
    def test_get_navigation_last(self):
        last = self.a.get_navigation_last()
        self.assertEquals('p', last.id)

        last = self.c.get_navigation_last()
        self.assertEquals('p', last.id)

    def test_get_navigation_next(self):
        next = self.a.get_navigation_next()
        self.assertEquals('b', next.id)

        next = self.c.get_navigation_next()
        self.assertEquals('d', next.id)
        
        next = self.f.get_navigation_next()
        self.assertEquals('g', next.id)

        next = self.l.get_navigation_next()
        self.assertEquals('m', next.id)

        next = self.i.get_navigation_next()
        self.assertEquals('j', next.id)

        next = self.b.get_navigation_next()
        self.assertEquals('c', next.id)

        next = self.g.get_navigation_next()
        self.assertEquals('h', next.id)
        
        next = self.o.get_navigation_next()
        self.assertEquals('p', next.id)


    def test_get_navigation_prev(self):
        prev = self.a.get_navigation_prev()
        self.assertEquals(None, prev)

        prev = self.d.get_navigation_prev()
        self.assertEquals('c', prev.id)
    
        prev = self.h.get_navigation_prev()
        self.assertEquals('g', prev.id)

        prev = self.g.get_navigation_prev()
        self.assertEquals('f', prev.id)

        prev = self.l.get_navigation_prev()
        self.assertEquals('k', prev.id)

        prev = self.o.get_navigation_prev()
        self.assertEquals('n', prev.id)

        prev = self.p.get_navigation_prev()
        self.assertEquals('o', prev.id)

class SecondTreeTestCase(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
    
        self.a = self.add_folder(
            self.root, 
            'a',
            'A')

        self.b = self.add_folder(
            self.a,
            'c',
            'C')

        self.c = c = self.add_document(self.b, 'c', 'Document C')
        self.d = d = self.add_document(self.b, 'd', 'Document D')
        self.e = e = self.add_document(self.a, 'e', 'Document E')
        
        for doc in [c,d,e]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

    def test_get_navigation_prev(self):
        prev = self.e.get_navigation_prev()
        self.assertEquals('d', prev.id)

class TreeWithPublicationsTestCase(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        
        self.root.manage_addProduct['Silva'].manage_addPublication('a', 'A')
        self.a = self.root.a
        
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
        
        self.root.a.h.manage_addProduct['Silva']\
            .manage_addPublication('j', 'J')
        self.j = self.root.a.h.j
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
        
        for doc in [d,e,f,i,k,l,p, i1,i2]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

    def testget_navigation_next(self):
        next = self.i.get_navigation_next()
        self.assertEquals('m', next.id)
    
class AdvancedTreeTestCase(SilvaTestCase.SilvaTestCase):
   
    def afterSetUp(self):
        
        self.root.manage_addProduct['Silva'].manage_addPublication('a', 'A')
        self.a = self.root.a
        
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
        
        for doc in [d,e,f,i,k,l,p, i1,i2]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

        self.url = 'http://nohost/root/'    
    
    def _helper(self, expected, obj):
        d = obj.get_navigation_links()
        keys = ['top', 'first', 'prev', 'next', 'last', 'up']
        for key in keys:
            if not expected.has_key(key):
                self.assert_(not d.has_key(key),\
                "not expected key: [%s] for id: %s" %(key, obj.id))
                continue
            if key == 'up':
                self.assertEquals('..', d['up'])
                continue
            self.assertEquals(expected[key], d[key].id)
    
    def make_dict(self, **kwargs):
        return kwargs

    def test_get_navigation_links_a(self):
        mapping = self.make_dict(next='b', last='p')
        self._helper(mapping, self.a)

    def test_get_navigation_links_b(self):
        mapping = self.make_dict(top='a', first='a', prev='a', next='c',
        last='p', up='..')
        self._helper(mapping, self.b)

    def test_get_navigation_links_c(self):
        mapping = self.make_dict(top='a', first='a', prev='b', next='d',
            last='p', up='..')
        self._helper(mapping, self.c)

    def test_get_navigation_links_d(self):
        mapping = self.make_dict(top='a', first='a', prev='c', next='e',
            last='p', up='..')
        self._helper(mapping, self.d)

    def test_get_navigation_links_e(self):
        mapping = self.make_dict(top='a', first='a', prev='d', next='f',
            last='p', up='..')
        self._helper(mapping, self.e)
    
    def test_get_navigation_links_f(self):
        mapping = self.make_dict(top='a', first='a', prev='e', next='g',
            last='p', up='..')
        self._helper(mapping, self.f)
   
    def test_get_navigation_links_g(self):
        mapping = self.make_dict(top='a', first='a', prev='f', next='h',
            last='p', up='..')
        self._helper(mapping, self.g)
    
    def test_get_navigation_links_h(self):
        mapping = self.make_dict(top='a', first='a', prev='g', next='i',
            last='p', up='..')
        self._helper(mapping, self.h)
   
    def test_get_navigation_links_i(self):
        mapping = self.make_dict(top='a', first='a', prev='h', next='j',
            last='p', up='..')
        self._helper(mapping, self.i)
   
    def test_get_navigation_links_j(self):
        mapping = self.make_dict(top='a', first='a', prev='i', next='k',
            last='p', up='..')
        self._helper(mapping, self.j)
    
    def test_get_navigation_links_k(self):
        mapping = self.make_dict(top='a', first='a', prev='j', next='l',
            last='p', up='..')
        self._helper(mapping, self.k)
        
    def test_get_navigation_links_l(self):
        mapping = self.make_dict(top='a', first='a', prev='k', next='m',
            last='p', up='..')
        self._helper(mapping, self.l)
   
    def test_get_navigation_links_m(self):
        mapping = self.make_dict(top='a', first='a', prev='l', next='n',
            last='p', up='..')
        self._helper(mapping, self.m)

    def test_get_navigation_links_n(self):
        mapping = self.make_dict(top='a', first='a', prev='m', next='o', 
            last='p', up='..')
        self._helper(mapping, self.n)

    def test_get_navigation_links_o(self):
        mapping = self.make_dict(top='a', first='a', prev='n', next='p',
            last='p', up='..')
        self._helper(mapping, self.o)
        
    def test_get_navigation_links_p(self):
        mapping = self.make_dict(top='a', first='a', prev='o', up='..')
        self._helper(mapping, self.p)
        
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

    def test_get_navigation_links(self):
        # test when viewing root, with an index
        links = self.root.get_navigation_links()
        self.assertEquals(self.f, links['last'])
        self.assertEquals(self.a, links['next'])
        self.assertEquals(2, len(links))
        
        # test when viewing doc e, which is the last
        links = self.root.a.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.root, links['prev'])
        self.assertEquals(self.b, links['next'])
        self.assertEquals(self.f, links['last'])
        self.assertEquals(6, len(links))
        
        # test when viewing doc d, which is the middle
        links = self.root.d.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.c, links['prev'])
        self.assertEquals(self.e, links['next'])
        self.assertEquals(self.f, links['last'])
        self.assertEquals(6, len(links))
        
        # test when viewing doc e, which is the last document
        links = self.root.f.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.e, links['prev'])
        self.assertEquals(4, len(links))

        # test when viewing at the second doc (b)
        links = self.root.b.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.a, links['prev'])
        self.assertEquals(self.c, links['next'])
        self.assertEquals(self.f, links['last'])
        self.assertEquals(6, len(links))
        
        # test when viewing at the second doc (e)
        links = self.root.e.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.d, links['prev'])
        self.assertEquals(self.f, links['next'])
        self.assertEquals(self.f, links['last'])
        self.assertEquals(6, len(links))
    
class SubFolderTestCase(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        # folder with one document
        self.folder = self.add_folder(
            self.root,
            'folder',
            'Folder2')
        
        # subfolder with two documents
        self.subfolder =  self.add_folder(
            self.folder, 
            'subfolder',
            'Subfolder of Folder2')
        
        self.a = a = self.add_document(self.folder, 'a', 'Document A')
        self.b = b = self.add_document(self.subfolder, 'b', 'Document B')
        self.c = c = self.add_document(self.subfolder, 'c', 'Document C')

        for doc in [a,b,c]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()
        
    def test_get_navigation_links(self):
        # test folder2
        links = self.root.get_navigation_links()
        self.assertEquals(self.folder, links['next'])
        self.assertEquals(self.a, links['last'])
        self.assertEquals(2, len(links))
        
        # test subfolder
        links = self.root.folder.subfolder.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.folder, links['prev'])
        self.assertEquals(self.b, links['next'])
        self.assertEquals(self.a, links['last'])
        self.assertEquals(6, len(links))

        # test doc a
        links = self.root.folder.a.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.c, links['prev'])
        self.assertEquals(4, len(links))

class IndexerTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        # folder with and Indexer and one document
        self.folder = self.add_folder(
            self.root,
            'folder',
            'Folder with an Auto TOC',
            policy_name='Silva AutoTOC')

        self.a = a = self.add_document(self.folder, 'a', 'Document A')
        self.root.manage_addProduct['Silva'].manage_addIndexer('indexer',
        'Title')
        

    def test_get_navigation_links(self):
        # test folder 3 with AutoTOC and unapproved document
        links = self.root.folder.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.root, links['prev'])
        self.assertEquals('http://nohost/root/indexer',
            links['next'].absolute_url())
        self.assertEquals('http://nohost/root/indexer',
            links['last'].absolute_url())
        self.assertEquals(6, len(links))
        
       
    def test_get_navigation_links2(self):
        links = self.root.indexer.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.folder, links['prev'])

class SubFolderIndexerTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self.folder = self.add_folder(
            self.root,
            'folder',
            'Folder with an Indexer',
            policy_name='Silva AutoTOC')
        self.subfolder = self.add_folder(
            self.folder, 
            'subfolder',
            'Subfolder')

        self.a = a = self.add_document(self.folder, 'a', 'Document A')
        self.b = b = self.add_document(self.folder, 'b', 'Document B')
        self.root.manage_addProduct['Silva'].manage_addIndexer('foobar',
        'Title')
        self.root.folder.subfolder.manage_addProduct['Silva']\
            .manage_addPublication('publication', 'MyPublication')
        self.root.folder.subfolder.publication.manage_addProduct['Silva']\
            .manage_addIndexer('newindexer', 'Title')

        for doc in [a, b]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            doc.approve_version()

    def test_get_navigation_links(self):
        # test folder 3 with AutoTOC and unapproved document
        links = self.root.folder.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.root, links['prev'])
        self.assertEquals(self.subfolder, links['next'])
        self.assertEquals('http://nohost/root/foobar',
            links['last'].absolute_url())
        self.assertEquals(6, len(links))

class MultipleIndexerTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self.root.manage_addProduct['Silva'].manage_addIndexer('indexer',
        'Title')
        self.root.manage_addProduct['Silva'].manage_addIndexer('secondindexer',
        'Second Title')
        
    def test_get_navigation_links(self):
        # test folder 3 with AutoTOC and unapproved document
        links = self.root.get_document_index_links(index_id='secondindexer')
        self.assertEquals('http://nohost/root/secondindexer',
            links['index'])
        
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

    def test_get_navigation_links(self):
        links = self.root.a.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.root, links['prev'])
        self.assertEquals(self.b, links['next'])
        self.assertEquals('http://nohost/root/asdf',
            links['last'].absolute_url())
        self.assertEquals(6, len(links))

        links = self.root.get_document_index_links(toc_id='dummy')
        self.assertEquals('http://nohost/root/dummy', links['contents'])

    def test_get_navigation_links_2(self):
        links = self.root.index.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.root, links['prev'])
        self.assertEquals(self.a, links['next'])
        self.assertEquals('http://nohost/root/asdf',
            links['last'].absolute_url())
        self.assertEquals(6, len(links))
        

    def test_get_document_index_links_on_toc(self):
        links = self.asdf.get_document_index_links()
        self.assertEquals('http://nohost/root/index', links['contents'])
        
class DocumentLinksTestCase(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        # chapters
        self.folder = self.add_folder(
            self.root,
            'folder',
            'Folder', 
            policy_name='Silva Document')
        
        # sections
        self.subfolder1 = self.add_folder(
            self.folder,
            'subf1',
            'Subfolder 1',
            policy_name='Silva Document')
        self.subfolder2 = self.add_folder(
            self.folder,
            'subf2',
            'Subfolder 2',
            policy_name='Silva Document')
            
        # subsections
        self.ssfolder1 = self.add_folder(
            self.subfolder1,
            'ssf1',
            'Subfolder 2',
            policy_name='Silva Document')
        self.ssfolder2 = self.add_folder(
            self.subfolder1,
            'ssf2',
            'Subfolder 2',
            policy_name='Silva Document')
        self.ssfolder3 = self.add_folder(
            self.subfolder2,
            'ssf3',
            'Subfolder 3',
            policy_name='Silva Document')

        # subsubsections
        self.sssfolder1 = self.add_folder(
            self.ssfolder1,
            'sssf1',
            'SubSubfolder 1',
            policy_name='Silva Document')
        self.sssfolder2 = self.add_folder(
            self.ssfolder1,
            'sssf2',
            'Subsubfolder 2',
            policy_name='Silva Document')
        self.sssfolder3 = self.add_folder(
            self.ssfolder3,
            'sssf3',
            'Subsubfolder 3',
            policy_name='Silva Document')

        self.a = a = self.add_document(self.folder, 'a', 'Document A')
        self.b = b = self.add_document(self.subfolder1, 'b', 'Document B')
        self.c = c = self.add_document(self.subfolder2, 'c', 'Document C')
        self.d = d = self.add_document(self.ssfolder1, 'd', 'Document D')
        self.e = e = self.add_document(self.ssfolder2, 'e', 'Document E')
        self.f = f = self.add_document(self.ssfolder3, 'f', 'Document F')
        self.g = g = self.add_document(self.sssfolder1, 'g', 'Document G')
        for doc in [a,b,c,d,e,f,g]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

        # Also publish index items:
        for folder in (self.folder, self.subfolder1, self.subfolder2,
                       self.ssfolder1, self.ssfolder2, self.ssfolder3,
                       self.sssfolder1, self.sssfolder2, self.sssfolder3):
            index = folder['index']
            index.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            index.approve_version()

    def test_document_links(self):
        r = self.root.get_document_chapter_links()
        chapters = [{'title':'Folder', 'url':'http://nohost/root/folder'}]
        self.assertEquals(chapters, r['chapter'])
        self.assertEquals(len(r), 1)
            
class DocumentLinksTestCase2(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        # chapters
        self.folder = self.add_folder(
            self.root,
            'folder',
            'Folder', 
            policy_name='Silva Document')
        
        # sections
        self.subfolder1 = self.add_folder(
            self.folder,
            'subf1',
            'Subfolder 1',
            policy_name='Silva Document')
        self.subfolder2 = self.add_folder(
            self.folder,
            'subf2',
            'Subfolder 2',
            policy_name='Silva Document')
            
        # subsections
        self.ssfolder1 = self.add_folder(
            self.subfolder1,
            'ssf1',
            'Subfolder 2',
            policy_name='Silva Document')
        self.ssfolder2 = self.add_folder(
            self.subfolder1,
            'ssf2',
            'Subfolder 2',
            policy_name='Silva Document')
        self.ssfolder3 = self.add_folder(
            self.subfolder2,
            'ssf3',
            'Subfolder 3',
            policy_name='Silva Document')

        # subsubsections
        self.sssfolder1 = self.add_folder(
            self.ssfolder1,
            'sssf1',
            'SubSubfolder 1',
            policy_name='Silva Document')
        self.sssfolder2 = self.add_folder(
            self.ssfolder1,
            'sssf2',
            'Subsubfolder 2',
            policy_name='Silva Document')
        self.sssfolder3 = self.add_folder(
            self.ssfolder3,
            'sssf3',
            'Subsubfolder 3',
            policy_name='Silva Document')

        self.a = a = self.add_document(self.folder, 'a', 'Document A')
        self.b = b = self.add_document(self.subfolder1, 'b', 'Document B')
        self.c = c = self.add_document(self.subfolder2, 'c', 'Document C')
        self.d = d = self.add_document(self.ssfolder1, 'd', 'Document D')
        self.e = e = self.add_document(self.ssfolder2, 'e', 'Document E')
        self.f = f = self.add_document(self.ssfolder3, 'f', 'Document F')
        self.g = g = self.add_document(self.sssfolder1, 'g', 'Document G')
        self.h = h = self.add_document(self.sssfolder2, 'h', 'Document H')

        for doc in [a,b,c,d,e,f,g,h]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

        # Also publish index items:
        for folder in (self.folder, self.subfolder1, self.subfolder2,
                       self.ssfolder1, self.ssfolder2, self.ssfolder3,
                       self.sssfolder1, self.sssfolder2):
            index = folder['index']
            index.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            index.approve_version()
            
    def test_document_links(self):
        r = self.root.get_document_chapter_links(depth=3)
        chapters = [{'title':'Folder', 'url':'http://nohost/root/folder'}]
        sections = [{'title':'Subfolder 1',
            'url':'http://nohost/root/folder/subf1'},
            {'title':'Subfolder 2',
            'url':'http://nohost/root/folder/subf2'}]
        subsections = [{'title':'Subfolder 2',
            'url':'http://nohost/root/folder/subf1/ssf1'},
            {'title':'Subfolder 2',
            'url':'http://nohost/root/folder/subf1/ssf2'},
            {'title':'Subfolder 3',
            'url':'http://nohost/root/folder/subf2/ssf3'}]
        subsubsections = [
            {'title':'SubSubfolder 1',
                'url':'http://nohost/root/folder/subf1/ssf1/sssf1'},
            {'title':'Subsubfolder 2',
                'url':'http://nohost/root/folder/subf1/ssf1/sssf2'}]
        self.assertEquals(chapters, r['chapter'])
        self.assertEquals(sections, r['section'])
        self.assertEquals(subsections, r['subsection'])
        self.assertEquals(subsubsections, r['subsubsection'])
        self.assertEquals(len(r), 4)

class DocumentLinksTestCase3(SilvaTestCase.SilvaTestCase):
    
    def afterSetup(self):
        self.index = index = self.add_document(self.root, 'index', 'INDEX')
        index.set_unapproved_version_publication_datetime(DateTime() - 1)
        index.approve_version()
        # chapters
        self.folder = self.add_folder(
            self.root,
            'folder',
            'Folder', 
            policy_name='Silva Document')
        
        # sections
        self.subfolder1 = self.add_folder(
            self.folder,
            'subf1',
            'Subfolder 1',
            policy_name='Silva Document')
        self.subfolder2 = self.add_folder(
            self.folder,
            'subf2',
            'Subfolder 2',
            policy_name='Silva Document')

    def test_document_links(self):
        r = self.root.get_document_chapter_links()
        self.assertEquals(r, {})

class DocumentLinksTestCaseDepth(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        # chapters
        self.folder = self.add_folder(
            self.root,
            'folder',
            'Folder', 
            policy_name='Silva Document')
        
        # sections
        self.subfolder1 = self.add_folder(
            self.folder,
            'subf1',
            'Subfolder 1',
            policy_name='Silva Document')
        self.subfolder2 = self.add_folder(
            self.folder,
            'subf2',
            'Subfolder 2',
            policy_name='Silva Document')
            
        # subsections
        self.ssfolder1 = self.add_folder(
            self.subfolder1,
            'ssf1',
            'Subfolder 2',
            policy_name='Silva Document')
        self.ssfolder2 = self.add_folder(
            self.subfolder1,
            'ssf2',
            'Subfolder 2',
            policy_name='Silva Document')
        self.ssfolder3 = self.add_folder(
            self.subfolder2,
            'ssf3',
            'Subfolder 3',
            policy_name='Silva Document')

        # subsubsections
        self.sssfolder1 = self.add_folder(
            self.ssfolder1,
            'sssf1',
            'SubSubfolder 1',
            policy_name='Silva Document')
        self.sssfolder2 = self.add_folder(
            self.ssfolder1,
            'sssf2',
            'Subsubfolder 2',
            policy_name='Silva Document')
        self.sssfolder3 = self.add_folder(
            self.ssfolder3,
            'sssf3',
            'Subsubfolder 3',
            policy_name='Silva Document')
        
        self.a = a = self.add_document(self.folder, 'a', 'Document A')
        self.b = b = self.add_document(self.subfolder1, 'b', 'Document B')
        self.c = c = self.add_document(self.subfolder2, 'c', 'Document C')
        self.d = d = self.add_document(self.ssfolder1, 'd', 'Document D')
        self.e = e = self.add_document(self.ssfolder2, 'e', 'Document E')
        self.f = f = self.add_document(self.ssfolder3, 'f', 'Document F')
        self.g = g = self.add_document(self.sssfolder1, 'g', 'Document G')
        self.h = h = self.add_document(self.sssfolder2, 'h', 'Document H')

        for doc in [a,b,c,d,e,f,g,h]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

        # Also publish index items:
        for folder in (self.folder, self.subfolder1, self.subfolder2,
                       self.ssfolder1, self.ssfolder2, self.ssfolder3,
                       self.sssfolder1, self.sssfolder2, self.sssfolder3):
            index = folder['index']
            index.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            index.approve_version()

    def test_document_links(self):
        r = self.root.get_document_chapter_links(depth=1)
        chapters = [{'title':'Folder', 'url':'http://nohost/root/folder'}]
        sections = [{'title':'Subfolder 1',
            'url':'http://nohost/root/folder/subf1'},
            {'title':'Subfolder 2',
            'url':'http://nohost/root/folder/subf2'}]
        self.assertEquals(chapters, r['chapter'])
        self.assertEquals(sections, r['section'])
        self.assertEquals(len(r), 2)

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

    def test_get_navigation_links(self):
        # test martijn situation
        links = self.root.get_navigation_links()
        self.assertEquals(self.tertius, links['next'])
        self.assertEquals(self.tertius, links['last'])
        self.assertEquals(2, len(links))

        links = self.root.index.get_navigation_links()
        self.assertEquals('..', links['up'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['prev'])
        self.assertEquals(self.tertius, links['next'])
        self.assertEquals(self.tertius, links['last'])
        self.assertEquals(6, len(links))
        
        links = self.root.tertius.get_navigation_links()
        self.assertEquals('..', links['up'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['prev'])
        self.assertEquals(4, len(links))

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

    def test_get_navigation_links(self):
        # test martijn situation
        links = self.root.get_navigation_links()
        self.assertEquals(self.secundus, links['next'])
        self.assertEquals(self.tertius, links['last'])
        self.assertEquals(2, len(links))
    
        links = self.root.tertius.get_navigation_links()
        self.assertEquals(self.root, links['top'])
        self.assertEquals(self.root, links['first'])
        self.assertEquals('..', links['up'])
        self.assertEquals(self.secundus, links['prev'])
        self.assertEquals(4, len(links))

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SimpleTestCase))
    suite.addTest(unittest.makeSuite(SecondTreeTestCase))
    suite.addTest(unittest.makeSuite(TreeWithPublicationsTestCase))
    suite.addTest(unittest.makeSuite(AdvancedTreeTestCase))
    suite.addTest(unittest.makeSuite(SubFolderTestCase))
    suite.addTest(unittest.makeSuite(SubFolderIndexerTestCase))
    suite.addTest(unittest.makeSuite(MultipleIndexerTestCase))
    suite.addTest(unittest.makeSuite(DocumentLinksTestCase))
    suite.addTest(unittest.makeSuite(DocumentLinksTestCase2))
    suite.addTest(unittest.makeSuite(DocumentLinksTestCase3))
    suite.addTest(unittest.makeSuite(DocumentLinksTestCaseDepth))
    suite.addTest(unittest.makeSuite(MartijnTestCase))
    suite.addTest(unittest.makeSuite(MartijnSecondTestCase))
    return suite

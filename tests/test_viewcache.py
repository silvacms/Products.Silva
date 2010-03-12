# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import SilvaTestCase

import time
from DateTime import DateTime


class ViewCacheTestCase(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.add_document(self.root, 'document', 'Document')
        self.document = self.root.document

    def beforeTearDown(self):
        pass

    def test_notPublished(self):
        doc = self.document
        # not published
        self.assertEquals(doc.get_viewable(), None)
        self.assert_(not doc.is_cached())

    def test_published(self):
        # doc gets published, use cache
        doc = self.document
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        doc.view()
        self.assert_(doc.is_cached())

    def test_notCacheable(self):
        # doc not cacheable
        doc = self.document
        dom = doc.get_editable().content
        dom.documentElement.appendChild(dom.createElement('code'))
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        doc.view()
        self.assert_(not doc.is_cached())

    def test_republish(self):
        # new publication of doc, cache is invalid
        doc = self.document
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        doc.view()
        doc.close_version()
        doc.create_copy()
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        self.assert_(not doc.is_cached())
        doc.view()
        self.assert_(doc.is_cached())

    def test_closed(self):
        # idem for closed
        doc = self.document
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        doc.view()
        doc.close_version()
        self.assert_(not doc.is_cached())

    def test_globalRefresh(self):
        # refreshtime is set, cache is invalid
        doc = self.document
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        data = doc.view()
        self.assert_(doc.is_cached())
        self.root.service_extensions.refresh_caches()
        self.assert_(not doc.is_cached())
        self.assertEquals(data, doc.view())
        self.assert_(doc.is_cached())

    def test_nowIsCacheable(self):
        # publication was not cacheable, but new version is
        doc = self.document
        dom = doc.get_editable().content
        dom.documentElement.appendChild(dom.createElement('code'))
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        data = doc.view()
        self.assert_(not doc.is_cached())
        doc.create_copy()
        dom = doc.get_editable().content
        dom.documentElement.removeChild(dom.documentElement.firstChild)
        dom.documentElement.appendChild(dom.createElement('p'))
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        self.assertNotEquals(data, doc.view())
        self.assert_(doc.is_cached())

    def test_nowIsNotCacheable(self):
        # publication was cacheable, but new version is not
        doc = self.document
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        data = doc.view()
        self.assert_(doc.is_cached())
        doc.create_copy()
        dom = doc.get_editable().content
        dom.documentElement.appendChild(dom.createElement('code'))
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        self.assertNotEquals(data, doc.view())
        self.assert_(not doc.is_cached())

    def test_publishInFuture(self):
        doc = self.document
        # create and publish a document
        now = DateTime()
        dom1 = doc.get_editable().content
        dom1.documentElement.appendChild(dom1.createElement('p'))
        doc.set_unapproved_version_publication_datetime(now - 3600)
        doc.approve_version()
        data = doc.view()

        # create copy and edit
        now = DateTime()
        doc.create_copy()
        dom2 = doc.get_editable().content
        dom2.documentElement.appendChild(dom2.createElement('heading'))
        # we publish the new version in the futur
        doc.set_unapproved_version_publication_datetime(now + 3600)
        doc.approve_version()
        # but still see the old one publish
        self.assert_(doc.is_cached())
        self.assertEquals(data, doc.view())

        # if we take back our version and publish it in the past, we
        # will see the new version
        doc.unapprove_version()
        doc.set_unapproved_version_publication_datetime(now - 3600)
        doc.approve_version()
        self.assert_(not doc.is_cached())
        self.assertNotEquals(data, doc.view())


class ViewCacheVirtualHostTestCase(ViewCacheTestCase):
    def afterSetUp(self):
        # Run all tests in a virtual host setup:
        # first setup a folder structure to be able to test
        # virtual hosts.
        self.add_folder(self.root, 'vhost1', 'Virtual Host One')
        self.add_folder(self.root, 'level1', 'Level One')
        self.add_folder(self.root.level1, 'level2', 'Level Two')
        self.add_folder(
            self.root.level1.level2, 'vhost2', 'Virtual Host Two')
        self.add_folder(
            self.root.level1.level2.vhost2, 'level3', 'Level Three')
        for container in [
                self.root,
                self.root.vhost1,
                self.root.level1,
                self.root.level1.level2,
                self.root.level1.level2.vhost2]:
            if not 'index' in container.objectIds():
                self.add_document(
                    container, 'index', 'Index of %s' % container.id)
        self.add_document(
            container, 'anotherdoc', 'Another doc of %s' % container.id)
        # Get REQUEST in shape
        request = self.request = self.app.REQUEST
        request['PARENTS'] = [self.root.level1.level2.vhost2]
        request.setServerURL(
            protocol='http', hostname='foo.bar.com', port='80')
        request.setVirtualRoot(('', 'root', 'level1', 'level2', 'vhost2'))
        self.document = self.root.level1.level2.vhost2.index

    def test_cachedDocumentsWithLinks(self):
        doc = self.root.level1.level2.vhost2.index
        dom = doc.get_editable().content
        # Create a paragraph with link elements, since link elements will be
        # clearly different for different virtual hosts
        p = dom.createElement('p')
        dom.documentElement.appendChild(p)
        p.appendChild(dom.createElement('link'))
        p.appendChild(dom.createElement('link'))
        p.childNodes[0].setAttribute('url', 'anotherdoc')
        p.childNodes[1].setAttribute('url', '/root/level1/index')
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        self.assert_(not doc.is_cached())
        data1 = doc.view()
        self.assert_(doc.is_cached())
        # Get REQUEST in shape for different virtual host
        request = self.request
        request['PARENTS'] = [self.app]
        request.setServerURL(
            protocol='http', hostname='baz.bar.com', port='80')
        request.setVirtualRoot(('',))
        self.assert_(not doc.is_cached())
        data2 = doc.view()
        self.assert_(doc.is_cached())
        self.assertNotEquals(data1, data2)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ViewCacheTestCase))
    suite.addTest(unittest.makeSuite(ViewCacheVirtualHostTestCase))
    return suite


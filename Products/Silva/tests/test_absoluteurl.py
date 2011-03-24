# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope import component

from Products.Silva.testing import FunctionalLayer
from Products.Silva.tests.helpers import enable_preview, reset_preview

from silva.core.views.interfaces import ISilvaURL


class AbsoluteURLTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        """Create some contents for testing:

        root
        |-- publication
        |   `-- folder
        |       `-- doc2
        `-- doc
        """

        self.publication = self.add_publication(self.root, 'publication', u'Test Publication')
        self.folder = self.add_folder(self.publication, 'folder', u'Test Folder')
        self.doc = self.add_document(self.root, 'doc', u'Test Document')
        self.doc2 = self.add_document(self.folder, 'doc2', u'Test Document 2')


    def get_absolute_url(self, content):
        abs_url = component.getMultiAdapter((content, self.root.REQUEST), ISilvaURL)
        self.failUnless(verifyObject(ISilvaURL, abs_url))
        return abs_url

    def test_url(self):
        self.failUnless(ISilvaURL.extends(IAbsoluteURL))
        # On publication
        abs_url = self.get_absolute_url(self.publication)
        self.assertEqual(str(abs_url),
                         'http://nohost/root/publication')
        self.assertEqual(abs_url(),
                         'http://nohost/root/publication')
        self.assertEqual(abs_url.preview(),
                         'http://nohost/root/++preview++/publication')

        enable_preview(self.root)
        self.assertEqual(str(abs_url),
                         'http://nohost/root/++preview++/publication')
        self.assertEqual(abs_url(),
                         'http://nohost/root/++preview++/publication')
        reset_preview(self.root)

        # On root
        abs_url = self.get_absolute_url(self.root)
        self.assertEqual(str(abs_url),
                         'http://nohost/root')
        self.assertEqual(abs_url(),
                         'http://nohost/root')
        self.assertEqual(abs_url.preview(),
                         'http://nohost/root/++preview++')

        enable_preview(self.root)
        self.assertEqual(str(abs_url),
                         'http://nohost/root/++preview++')
        self.assertEqual(abs_url(),
                         'http://nohost/root/++preview++')
        reset_preview(self.root)

        # On document 2
        abs_url = self.get_absolute_url(self.doc2)
        self.assertEqual(str(abs_url),
                         'http://nohost/root/publication/folder/doc2')
        self.assertEqual(abs_url(),
                         'http://nohost/root/publication/folder/doc2')
        self.assertEqual(abs_url.preview(),
                         'http://nohost/root/++preview++/publication/folder/doc2')

        enable_preview(self.root)
        self.assertEqual(str(abs_url),
                         'http://nohost/root/++preview++/publication/folder/doc2')
        self.assertEqual(abs_url(),
                         'http://nohost/root/++preview++/publication/folder/doc2')
        reset_preview(self.root)


    def test_breadcrumbs(self):
        # On publication
        abs_url = self.get_absolute_url(self.publication)
        self.assertEqual(abs_url.breadcrumbs(),
                         ({'url': 'http://nohost/root', 'name': 'root'},
                          {'url': 'http://nohost/root/publication', 'name': u'Test Publication'}))

        enable_preview(self.root)
        self.assertEqual(abs_url.breadcrumbs(),
                         ({'url': 'http://nohost/root/++preview++', 'name': 'root'},
                          {'url': 'http://nohost/root/++preview++/publication', 'name': u'Test Publication'}))
        reset_preview(self.root)

        # On root
        abs_url = self.get_absolute_url(self.root)
        self.assertEqual(abs_url.breadcrumbs(),
                         ({'url': 'http://nohost/root', 'name': 'root'},))

        enable_preview(self.root)
        self.assertEqual(abs_url.breadcrumbs(),
                         ({'url': 'http://nohost/root/++preview++', 'name': 'root'},))
        reset_preview(self.root)

        # On document 2
        abs_url = self.get_absolute_url(self.doc2)
        self.assertEqual(abs_url.breadcrumbs(),
                         ({'url': 'http://nohost/root', 'name': 'root'},
                          {'url': 'http://nohost/root/publication', 'name': u'Test Publication'},
                          {'url': 'http://nohost/root/publication/folder', 'name': u'Test Folder'},
                          {'url': 'http://nohost/root/publication/folder/doc2', 'name': 'doc2'}))

        enable_preview(self.root)
        self.assertEqual(abs_url.breadcrumbs(),
                         ({'url': 'http://nohost/root/++preview++', 'name': 'root'},
                          {'url': 'http://nohost/root/++preview++/publication', 'name': u'Test Publication'},
                          {'url': 'http://nohost/root/++preview++/publication/folder', 'name': u'Test Folder'},
                          {'url': 'http://nohost/root/++preview++/publication/folder/doc2', 'name': 'doc2'}))
        reset_preview(self.root)


    def test_traverse(self):
        abs_url = self.root.restrictedTraverse('@@absolute_url')
        self.failUnless(verifyObject(ISilvaURL, abs_url))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AbsoluteURLTestCase))
    return suite



# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.interface.verify import verifyObject
from silva.core.interfaces import IHaunted

from Products.Silva.testing import FunctionalLayer


class HauntedTestCase(unittest.TestCase):
    """Test the Haunted adapter.
    """
    layer = FunctionalLayer

    def setUp(self):
        """Content tree:

        /doc
        /publication
        /publication/folder
        /ghost
        /link

        """
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', u'Test Document')
        factory.manage_addPublication('publication', u'Test Publication')
        factory.manage_addGhost('ghost', None, haunted=self.root.document)
        factory.manage_addLink('link', u'Test Link')

        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addFolder('folder', u'Test Folder')

    def test_get_haunting(self):
        # No adapter for non-content or containers objects
        self.assertRaises(TypeError, IHaunted, self.root.service_catalog)
        self.assertRaises(TypeError, IHaunted, self.root.publication.folder)
        self.assertRaises(TypeError, IHaunted, self.root.publication)

        # Test getting an adapter for content
        self.assertTrue(verifyObject(IHaunted, IHaunted(self.root.document)))
        self.assertTrue(verifyObject(IHaunted, IHaunted(self.root.link)))
        self.assertTrue(verifyObject(IHaunted, IHaunted(self.root.ghost)))

        self.assertEqual(
            list(IHaunted(self.root.document).getHaunting()),
            [self.root.ghost])
        self.assertEqual(
            list(IHaunted(self.root.link).getHaunting()),
            [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HauntedTestCase))
    return suite

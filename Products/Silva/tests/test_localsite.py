# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import ISiteManager
from zope.interface.verify import verifyObject
from zope import component

from Products.Silva.testing import FunctionalLayer


class LocalSiteTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_localsite_on_root(self):
        # ISiteManager is an adapter on publication to manage local sites.
        manager = ISiteManager(self.root)
        self.assertTrue(verifyObject(ISiteManager, manager))

        # By default the root is a local site
        self.assertTrue(manager.is_site())
        # And you can't disable it/play with it
        self.assertRaises(ValueError, manager.delete_site)
        self.assertRaises(ValueError, manager.make_site)

    def test_localsite_on_publication(self):
        # Now we add a publication
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'publication')

        # We can get an adapter on it.
        manager = ISiteManager(self.root.publication)
        self.assertTrue(verifyObject(ISiteManager, manager))

        # It's not a local site by default.
        self.assertFalse(manager.is_site())
        # So we can't disable it.
        self.assertRaises(ValueError, manager.delete_site)
        # But we can enable it.
        manager.make_site()
        self.assertTrue(manager.is_site())
        # Only one time
        self.assertRaises(ValueError, manager.make_site)

        # We can add a local service in it.
        factory = self.root.publication.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationService('service_customization')
        self.assertTrue(hasattr(self.root.publication, 'service_customization'))
        # We need to delete our service first
        self.root.publication.manage_delObjects(['service_customization',])

        # And disable it.
        manager.delete_site()
        self.assertFalse(manager.is_site())
        self.assertRaises(ValueError, manager.delete_site)

    def test_localsite_on_invalid_content(self):
        # Create a document
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'document')

        # Can't be a local site.
        manager = component.queryAdapter(self.root.document, ISiteManager)
        self.assertEqual(manager, None)

        # Create a folder
        factory.manage_addFolder('folder', 'Folderr')

        # Can't be a local site.
        manager = component.queryAdapter(self.root.folder, ISiteManager)
        self.assertEqual(manager, None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LocalSiteTestCase))
    return suite


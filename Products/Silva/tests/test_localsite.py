# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

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
        self.assertTrue(manager.isSite())
        # And you can't disable it/play with it
        self.assertRaises(ValueError, manager.deleteSite)
        self.assertRaises(ValueError, manager.makeSite)

    def test_localsite_on_publication(self):
        # Now we add a publication
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'publication')

        # We can get an adapter on it.
        manager = ISiteManager(self.root.publication)
        self.assertTrue(verifyObject(ISiteManager, manager))

        # It's not a local site by default.
        self.assertFalse(manager.isSite())
        # So we can't disable it.
        self.assertRaises(ValueError, manager.deleteSite)
        # But we can enable it.
        manager.makeSite()
        self.assertTrue(manager.isSite())
        # Only one time
        self.assertRaises(ValueError, manager.makeSite)

        # We can add a local service in it.
        factory = self.root.publication.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationService('service_customization')
        self.assertTrue(hasattr(self.root.publication, 'service_customization'))
        # We need to delete our service first
        self.root.publication.manage_delObjects(['service_customization',])

        # And disable it.
        manager.deleteSite()
        self.assertFalse(manager.isSite())
        self.assertRaises(ValueError, manager.deleteSite)

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


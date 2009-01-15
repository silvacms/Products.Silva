# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import SilvaTestCase

from zope.interface.verify import verifyObject
from zope import component

from Products.Silva.interfaces import ISiteManager

class LocalSiteTest(SilvaTestCase.SilvaTestCase):

    def test_localsite_on_root(self):
        # ISiteManager is an adapter on publication to manage local sites.
        manager = ISiteManager(self.root)
        self.failUnless(verifyObject(ISiteManager, manager))

        # By default the root is a local site
        self.failUnless(manager.isSite())
        # And you can't disable it/play with it
        self.assertRaises(ValueError, manager.deleteSite)
        self.assertRaises(ValueError, manager.makeSite)

    def test_localsite_on_publication(self):
        # Now we add a publication
        self.add_publication(self.root, 'publication', 'publication')

        # We can get an adapter on it.
        manager = ISiteManager(self.root.publication)
        self.failUnless(verifyObject(ISiteManager, manager))

        # It's not a local site by default.
        self.failIf(manager.isSite())
        # So we can't disable it.
        self.assertRaises(ValueError, manager.deleteSite)
        # But we can enable it.
        manager.makeSite()
        self.failUnless(manager.isSite())
        # Only one time
        self.assertRaises(ValueError, manager.makeSite)

        # We can add a local service in it.
        self.root.publication.manage_addProduct['silva.core.layout'].manage_addCustomizationService('service_customization')
        self.failUnless(hasattr(self.root.publication, 'service_customization'))
        # We need to delete our service first
        self.root.publication.manage_delObjects(['service_customization',])

        # And disable it.
        manager.deleteSite()
        self.failIf(manager.isSite())
        self.assertRaises(ValueError, manager.deleteSite)

    def test_localsite_on_invalid_content(self):
        # Create a document
        self.add_document(self.root, 'document', 'document')
        # Can't be a local site.
        manager = component.queryAdapter(self.root.document, ISiteManager)
        self.assertEqual(manager, None)

        # Create a folder
        self.add_folder(self.root, 'folder', 'folder')
        # Can't be a local site.
        manager = component.queryAdapter(self.root.folder, ISiteManager)
        self.assertEqual(manager, None)



import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LocalSiteTest))
    return suite


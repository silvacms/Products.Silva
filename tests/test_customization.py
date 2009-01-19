# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.component import getUtility
from zope.interface.verify import verifyObject
from zope.app.component.interfaces import ISite

from zExceptions import BadRequest
from five.localsitemanager import make_objectmanager_site

from silva.core.layout.interfaces import ICustomizationService, IViewManager
from Products.Silva.interfaces import IFolder, IContainer
from silva.core.layout.porto.interfaces import IPortoSkin, IPorto

import SilvaTestCase

class CustomizationServiceTest(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        factory = self.root.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationService('service_customization')

    def test_utility_only_in_local_site(self):
        # A service_customization can be added only in a local site.
        self.failUnless(ISite.providedBy(self.root))
        self.publication = self.add_publication(self.root, 'publication', 'Publication')
        self.failIf(ISite.providedBy(self.publication))
        factory = self.publication.manage_addProduct['silva.core.layout']
        self.assertRaises(BadRequest,
                          factory.manage_addCustomizationService,
                          'service_customization')

        # Now our publication become a local site.
        make_objectmanager_site(self.publication)
        self.failUnless(ISite.providedBy(self.publication))
        factory = self.publication.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationService('service_customization')
        self.failUnless(hasattr(self.publication, 'service_customization'))

    def test_utility(self):
        self.failUnless(hasattr(self.root, 'service_customization'))

        # Now we can fetch it
        utility = getUtility(ICustomizationService)
        self.failUnless(verifyObject(ICustomizationService, utility))

    def test_utility_available_interfaces(self):
        self.failUnless(hasattr(self.root, 'service_customization'))
        utility = getUtility(ICustomizationService)

        # We can list availables interfaces
        someDefaultInterfaces =  [u'Products.Silva.interfaces.content.IAsset',
                                  u'Products.Silva.interfaces.content.IContainer',
                                  u'Products.Silva.interfaces.content.IContent',
                                  u'Products.Silva.interfaces.content.IFile',
                                  u'Products.Silva.interfaces.content.IFolder',
                                  u'Products.Silva.interfaces.content.IGroup',
                                  u'Products.Silva.interfaces.content.IPublication',
                                  u'Products.Silva.interfaces.content.IRoot',
                                  u'Products.Silva.interfaces.content.ISilvaObject',
                                  u'Products.Silva.interfaces.content.IVersionedContent',
                                  u'Products.SilvaDocument.interfaces.IDocument',
                                  u'silva.core.layout.interfaces.ICustomizableMarker',
                                  u'silva.core.layout.interfaces.ICustomizableTag']
        foundInterfaces = utility.availablesInterfaces()
        for iface in someDefaultInterfaces:
            self.failUnless(iface in foundInterfaces)

        # We can restrain it to a sub set
        containerDefaultInterfaces = [u'Products.Silva.interfaces.content.IContainer',
                                      u'Products.Silva.interfaces.content.IFolder',
                                      u'Products.Silva.interfaces.content.IPublication',
                                      u'Products.Silva.interfaces.content.IRoot',]
        foundInterfaces = utility.availablesInterfaces(base=IContainer)
        for iface in containerDefaultInterfaces:
            self.failUnless(iface in foundInterfaces)

    def test_utility_available_layers(self):
        self.failUnless(hasattr(self.root, 'service_customization'))
        utility = getUtility(ICustomizationService)

        # Same goes for layers
        someDefaultLayers = [u'Products.SilvaLayout.browser.silvadefault.skin.ISilvaDefault',
                             u'Products.SilvaLayout.browser.silvalegacy.skin.ISilvaLegacy',
                             u'silva.core.layout.interfaces.ISMILayer',
                             u'silva.core.layout.interfaces.ISilvaLayer',
                             u'silva.core.layout.porto.interfaces.IPorto',
                             u'silva.core.layout.porto.interfaces.IPortoWithCSS',
                             u'zope.publisher.interfaces.browser.IDefaultBrowserLayer']
        foundLayers = utility.availablesLayers()
        for iface in someDefaultLayers:
            self.failUnless(iface in foundLayers)

        # We can restrain it to a sub set
        silvaNewStyleLayers = [u'silva.core.layout.porto.interfaces.IPorto',
                               u'silva.core.layout.porto.interfaces.IPortoWithCSS',]
        foundLayers = utility.availablesLayers(base=IPorto)
        for iface in silvaNewStyleLayers:
            self.failUnless(iface in foundLayers)

    def test_view_manager(self):
        # We are going to create a folder, and a document
        self.add_document(self.root, 'document', 'document')
        self.add_folder(self.root, 'folder', 'folder')

        manager = IViewManager(self.root.service_customization)
        self.failUnless(verifyObject(IViewManager, manager))



import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CustomizationServiceTest))
    return suite

# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from os.path import basename

# Zope 3
from zope.component import getUtility
from zope.interface.verify import verifyObject
from zope.app.component.interfaces import ISite

# Zope 2
from zExceptions import BadRequest
from five.localsitemanager import make_objectmanager_site

# Silva
from silva.core.layout.interfaces import ICustomizationService, \
    IViewManager, IViewInfo
from silva.core.layout.porto.interfaces import IPortoSkin, IPorto
from silva.core.interfaces.content import IFolder, IContainer

import SilvaTestCase


class CustomizationServiceTestCase(SilvaTestCase.SilvaTestCase):
    """Test service customization setup and methods.
    """

    def afterSetUp(self):
        factory = self.root.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationService('service_customization')

    def test_utility_only_in_local_site(self):
        # A service_customization can be added only in a local site.
        self.failUnless(ISite.providedBy(self.root))
        self.publication = self.add_publication(
            self.root, 'publication', 'Publication')
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
        someDefaultInterfaces =  [
            u'silva.core.interfaces.content.IAsset',
            u'silva.core.interfaces.content.IContainer',
            u'silva.core.interfaces.content.IContent',
            u'silva.core.interfaces.content.IFile',
            u'silva.core.interfaces.content.IFolder',
            u'silva.core.interfaces.content.IGroup',
            u'silva.core.interfaces.content.IPublication',
            u'silva.core.interfaces.content.IRoot',
            u'silva.core.interfaces.content.ISilvaObject',
            u'silva.core.interfaces.content.IVersionedContent',
            u'Products.SilvaDocument.interfaces.IDocument',
            u'silva.core.layout.interfaces.ICustomizableMarker',
            u'silva.core.layout.interfaces.ICustomizableTag']

        foundInterfaces = utility.availablesInterfaces()
        for iface in someDefaultInterfaces:
            self.failUnless(iface in foundInterfaces)

        # We can restrain it to a sub set
        containerDefaultInterfaces = [
            u'silva.core.interfaces.content.IContainer',
            u'silva.core.interfaces.content.IFolder',
            u'silva.core.interfaces.content.IPublication',
            u'silva.core.interfaces.content.IRoot',]

        foundInterfaces = utility.availablesInterfaces(base=IContainer)
        for iface in containerDefaultInterfaces:
            self.failUnless(iface in foundInterfaces)

    def test_utility_available_layers(self):
        self.failUnless(hasattr(self.root, 'service_customization'))
        utility = getUtility(ICustomizationService)

        # Same goes for layers
        someDefaultLayers = [
            u'Products.SilvaLayout.browser.silvadefault.skin.ISilvaDefault',
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
        silvaNewStyleLayers = [
            u'silva.core.layout.porto.interfaces.IPorto',
            u'silva.core.layout.porto.interfaces.IPortoWithCSS',]

        foundLayers = utility.availablesLayers(base=IPorto)
        for iface in silvaNewStyleLayers:
            self.failUnless(iface in foundLayers)

    def test_view_manager(self):
        # We are going to create a folder, and a document
        utility = getUtility(ICustomizationService)
        manager = IViewManager(utility)
        self.failUnless(verifyObject(IViewManager, manager))


class ViewEntryTestCase(SilvaTestCase.SilvaTestCase):
    """Test ViewEntry lookup and objects.
    """

    def afterSetUp(self):
        factory = self.root.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationService('service_customization')
        self.utility = getUtility(ICustomizationService)

    def test_grok_template(self):
        signature = "zope.interface.Interface:index.html:None:" \
            "silva.core.interfaces.content.ISilvaObject:" \
            "silva.core.layout.porto.interfaces.IPorto"
        manager = IViewManager(self.utility)
        view = manager.from_signature(signature)
        self.failIf(view is None)
        self.failUnless(verifyObject(IViewInfo, view))
        self.assertEqual(view.type_, 'Grok Page Template')
        self.assertEqual(view.name, 'index.html')
        self.assertEqual(
            view.for_,
            'silva.core.interfaces.content.ISilvaObject')
        self.assertEqual(
            view.layer,
            'silva.core.layout.porto.interfaces.IPorto')
        self.assertEqual(basename(view.template), 'maintemplate.pt')
        self.assertEqual(view.origin, None)
        self.assertEqual(manager.get_signature(view), signature)

    def test_five_template(self):
        signature = "zope.interface.Interface:object_lookup:None:" \
            "silva.core.interfaces.content.ISilvaObject:" \
            "zope.publisher.interfaces.browser.IDefaultBrowserLayer"
        manager = IViewManager(self.utility)
        view = manager.from_signature(signature)
        self.failIf(view is None)
        self.failUnless(verifyObject(IViewInfo, view))
        self.assertEqual(view.type_, 'Five Page Template')
        self.assertEqual(view.name, 'object_lookup')
        self.assertEqual(
            view.for_,
            'silva.core.interfaces.content.ISilvaObject')
        self.assertEqual(
            view.layer,
            'zope.publisher.interfaces.browser.IDefaultBrowserLayer')
        self.assertEqual(basename(view.template), 'object_lookup.pt')
        self.assertEqual(view.origin, None)
        self.assertEqual(manager.get_signature(view), signature)

    def test_grok_content_provider(self):
        signature = "zope.viewlet.interfaces.IViewletManager:footer:None:" \
            "silva.core.interfaces.content.ISilvaObject:" \
            "silva.core.layout.porto.interfaces.IPorto:" \
            "zope.publisher.interfaces.browser.IBrowserView"
        manager = IViewManager(self.utility)
        view = manager.from_signature(signature)
        self.failIf(view is None)
        self.failUnless(verifyObject(IViewInfo, view))
        self.assertEqual(view.type_, 'Grok Content Provider')
        self.assertEqual(view.name, 'footer')
        self.assertEqual(
            view.for_,
            'silva.core.interfaces.content.ISilvaObject')
        self.assertEqual(
            view.layer,
            'silva.core.layout.porto.interfaces.IPorto')
        self.assertEqual(basename(view.template), 'footer.pt')
        self.assertEqual(view.origin, None)
        self.assertEqual(manager.get_signature(view), signature)

    def test_grok_viewlet(self):
        signature = "zope.viewlet.interfaces.IViewlet:settingsbutton:None:" \
            "silva.core.interfaces.content.ISilvaObject:" \
            "silva.core.layout.interfaces.ISMILayer:" \
            "silva.core.smi.smi.PropertiesTab:" \
            "silva.core.smi.smi.SMIMiddleGroundManager"
        manager = IViewManager(self.utility)
        view = manager.from_signature(signature)
        self.failIf(view is None)
        self.failUnless(verifyObject(IViewInfo, view))
        self.assertEqual(view.type_, 'Grok Viewlet')
        self.assertEqual(view.name, 'settingsbutton')
        self.assertEqual(
            view.for_,
            'silva.core.interfaces.content.ISilvaObject')
        self.assertEqual(view.layer, 'silva.core.layout.interfaces.ISMILayer')
        self.assertEqual(basename(view.template), 'smibutton.pt')
        self.assertEqual(view.origin, None)
        self.assertEqual(manager.get_signature(view), signature)


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CustomizationServiceTestCase))
    suite.addTest(unittest.makeSuite(ViewEntryTestCase))
    return suite

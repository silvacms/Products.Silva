# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import Unauthorized

from zope.interface.interfaces import IInterface
from zope.interface.verify import verifyObject

from silva.core.layout.interfaces import IMarkManager, ICustomizableMarker, \
    ICustomizable

import SilvaTestCase


class CustomizationMarkerTest(SilvaTestCase.SilvaTestCase):

    def test_marker_on_root(self):
        manager = IMarkManager(self.root)
        self.failUnless(verifyObject(IMarkManager, manager))

        # By default, we got interfaces implemented by Root
        self.assertEqual(manager.usedInterfaces,
                         ['silva.core.interfaces.content.IFolder',
                          'silva.core.interfaces.content.IPublication',
                          'silva.core.interfaces.content.IRoot'])

        # And there is no marker used.
        self.assertEqual(manager.usedMarkers, [])
        # The base interfaces for markers is availables however.
        self.assertEqual(manager.availablesMarkers,
                         [u'silva.core.layout.interfaces.ICustomizableMarker'])


        # We can add a marker in ZODB
        factory = self.root.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationMarker('ITestMarker')
        self.failUnless('ITestMarker' in self.root.objectIds())
        marker = getattr(self.root, 'ITestMarker')

        # A marker is an interface which extend ICustomizableMarker,
        # so it's customizable
        self.failUnless(verifyObject(IInterface, marker))
        self.failUnless(marker.extends(ICustomizableMarker))
        self.failUnless(marker.extends(ICustomizable))

        # Marker have an markerId which gives it's identifier, we
        # should be the same than the interface __identifier__
        self.failUnless(marker.markerId(), u'marker:root.ITestMarker')
        self.failUnless(marker.__identifier__, u'marker:root.ITestMarker')

        # Now, we should see our marker in availables ones
        # Since our manager cache it's result, we need to recreate a new one.
        manager = IMarkManager(self.root)
        self.assertEqual(manager.availablesMarkers,
                         [u'marker:root.ITestMarker',
                          u'silva.core.layout.interfaces.ICustomizableMarker'])

        # We can assign a marker to the root
        manager.addMarker(u'marker:root.ITestMarker')

        # And we will have root object which provided this object
        self.failUnless(marker.providedBy(self.root))

        # And we will see changes in the manager
        manager = IMarkManager(self.root)
        self.assertEqual(manager.usedMarkers, [u'marker:root.ITestMarker'])
        self.assertEqual(manager.availablesMarkers,
                         [u'silva.core.layout.interfaces.ICustomizableMarker'])


        # Like we assign the marker, we can remove it.
        manager.removeMarker(u'marker:root.ITestMarker')

        # And it will disppear
        self.failIf(marker.providedBy(self.root))
        manager = IMarkManager(self.root)
        self.assertEqual(manager.usedMarkers, [])
        self.assertEqual(manager.availablesMarkers,
                         [u'marker:root.ITestMarker',
                          u'silva.core.layout.interfaces.ICustomizableMarker'])

        # We can delete the marker
        self.root.manage_delObjects(['ITestMarker',])

        # And it won't appear in the manager anymore (it's gone)
        manager = IMarkManager(self.root)
        self.assertEqual(manager.usedMarkers, [])
        self.assertEqual(manager.availablesMarkers,
                         [u'silva.core.layout.interfaces.ICustomizableMarker'])


    def test_marker_on_root_delete(self):
        # Here, we create a marker, and check that's it remerber which
        # object it mark. If you delete the marker, mark should
        # disppear on object before.

        factory = self.root.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationMarker('ITestMarker')
        self.failUnless('ITestMarker' in self.root.objectIds())
        marker = getattr(self.root, 'ITestMarker')

        # Set the mark on the root
        manager = IMarkManager(self.root)
        manager.addMarker(u'marker:root.ITestMarker')

        # The marker remerbers which object it have marked.
        self.assertEqual(marker.markedObjects(), [self.root,])

        # And the manager confirm that
        manager = IMarkManager(self.root)
        self.assertEqual(manager.usedMarkers, [u'marker:root.ITestMarker'])

        # Now, I delete the marker before removing from the object.
        self.root.manage_delObjects(['ITestMarker',])

        # And root have been updated
        manager = IMarkManager(self.root)
        self.assertEqual(manager.usedMarkers, [])
        self.assertEqual(manager.availablesMarkers,
                         [u'silva.core.layout.interfaces.ICustomizableMarker'])



    def test_customization_view(self):
        # There is a customization page to manage them on Silva
        # Folderish and VersionedContent

        self.assertRaises(
            Unauthorized, self.root.restrictedTraverse, 'manage_customization')

        # But of course, you need to be logged
        self.login(name=SilvaTestCase.user_manager)
        view = self.root.restrictedTraverse('manage_customization')()

        for implemented in ['silva.core.interfaces.content.IFolder',
                            'silva.core.interfaces.content.IPublication',
                            'silva.core.interfaces.content.IRoot']:
            self.failUnless(implemented in view)

        # You will have the same on Folder
        self.add_folder(self.root, 'folder', 'Folder')
        view = self.root.folder.restrictedTraverse('manage_customization')()
        self.failUnless('silva.core.interfaces.content.IFolder' in view)

        # And on a document
        self.add_document(self.root, 'document', 'Document')
        view = self.root.document.restrictedTraverse('manage_customization')()
        self.failUnless('Products.SilvaDocument.interfaces.IDocument' in view)

        self.logout()


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CustomizationMarkerTest))
    return suite


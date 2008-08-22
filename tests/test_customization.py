# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.component import getUtility
from zope.interface.verify import verifyObject

from silva.core.layout.interfaces import ICustomizationService

import SilvaTestCase

class CustomizationServiceTest(SilvaTestCase.SilvaTestCase):

    def test_utility(self):
        # This utility is not added by default, we need to do it.
        self.root.manage_addProduct['silva.core.layout'].manage_addCustomizationService('service_customization')
        
        # Now we can fetch it
        utility = getUtility(ICustomizationService)
        self.failUnless(verifyObject(ICustomizationService, utility))

        # We can list availables layers
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
        


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CustomizationServiceTest))
    return suite

# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from five.localsitemanager import make_objectmanager_site

from zope.app.component.hooks import clearSite
from zope.location.interfaces import ISite

from Products.Five.component import disableSite
from silva.core import interfaces

class SiteManager(grok.Adapter):

    grok.implements(interfaces.ISiteManager)
    grok.context(interfaces.IPublication)
    grok.require('zope2.ViewManagementScreens')

    def makeSite(self):
        if self.isSite():
            raise ValueError, 'Already a local site.'
        make_objectmanager_site(self.context)

    def deleteSite(self):
        if not self.isSite():
            raise ValueError, 'Not a local site.'
        if interfaces.IRoot.providedBy(self.context):
            raise ValueError, "Can't disable local site on Silva Root."
        sm = ISite(self.context).getSiteManager()
        if list(sm.registeredAdapters()):
            raise ValueError, 'Still have registered adapters.'
        if list(sm.registeredUtilities()):
            raise ValueError, 'Still have registered utilities.'
        disableSite(self.context)

    def isSite(self):
        return ISite.providedBy(self.context)



# Copyright (c) 2003-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from five.localsitemanager import make_objectmanager_site

from zope.app.component.hooks import clearSite
from zope.app.component.interfaces import ISite

from Products.Five.site.localsite import disableLocalSiteHook
from Products.Silva import interfaces

class SiteManager(grok.Adapter):

    grok.provides(interfaces.ISiteManager)
    grok.context(interfaces.IPublication)
    grok.require('zope2.ViewManagementScreens')

    def makeSite(self):
        if self.isSite():
            raise ValueError, 'Already a local site.'
        make_objectmanager_site(self.context)

    def unmakeSite(self):
        if not self.isSite():
            raise ValueError, 'Not a local site.'
        sm = ISite(self.context).getSiteManager()
        if list(sm.registeredAdapters()):
            raise ValueError, 'Still have registered adapters.'
        if list(sm.registeredUtilities()):
            raise ValueError, 'Still have registered utilities.'
        disableLocalSiteHook(self.context)
        clearSite()

    def isSite(self):
        return ISite.providedBy(self.context)



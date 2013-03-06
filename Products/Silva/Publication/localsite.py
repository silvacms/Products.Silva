# -*- coding: utf-8 -*-
# Copyright (c) 2003-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from five.localsitemanager import make_objectmanager_site
from zope.location.interfaces import ISite

from Products.Five.component import disableSite
from silva.core import interfaces
from silva.translations import translate as _


class SiteManager(grok.Adapter):
    grok.implements(interfaces.ISiteManager)
    grok.context(interfaces.IPublication)
    grok.require('zope2.ViewManagementScreens')

    def make_site(self):
        if self.is_site():
            raise ValueError(_(u'Already a local site.'))
        make_objectmanager_site(self.context)

    def delete_site(self):
        if not self.is_site():
            raise ValueError(_(u'Not a local site.'))
        if interfaces.IRoot.providedBy(self.context):
            raise ValueError(_(u"Can't disable local site on Silva Root."))
        sm = ISite(self.context).getSiteManager()
        if list(sm.registeredAdapters()):
            raise ValueError(_(u'Still have registered customizations.'))
        if list(sm.registeredUtilities()):
            raise ValueError(_(u'Still have registered services.'))
        disableSite(self.context)

    def is_site(self):
        return ISite.providedBy(self.context)

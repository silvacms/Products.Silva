# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass # Zope 2.12

# Silva
from Products.Silva.Publishable import Publishable
from Products.Silva import SilvaPermissions

from five import grok
from silva.core.interfaces import IContent


class Content(Publishable):
    grok.baseclass()
    grok.implements(IContent)
    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_default')
    def is_default(self):
        return self.id == 'index'

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_content')
    def get_content(self):
        """Get the content. Can be used with acquisition to get
        the 'nearest' content."""
        return self.aq_inner


InitializeClass(Content)


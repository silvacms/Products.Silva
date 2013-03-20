# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.SilvaObject import SilvaObject, ViewableObject

from five import grok
from silva.core.interfaces.content import IPublishable, INonPublishable
from silva.core.interfaces import IHTTPHeadersSettings


class NonPublishable(SilvaObject):
    """Base content which is not a published content in Silva. It
    doesn't appear in navigation, and is not ordered.
    """
    grok.baseclass()
    grok.implements(INonPublishable)



class Publishable(SilvaObject, ViewableObject):
    """Base content that can be published and ordered in Silva.
    """
    grok.baseclass()
    grok.implements(IPublishable)

    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_default')
    def is_default(self):
        """returns True if the SilvaObject is a default document
        """
        return False

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_published')
    def is_published(self):
        return True

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_approved')
    def is_approved(self):
        return False


InitializeClass(Publishable)


class HTTPHeadersSettings(grok.Annotation):
    """Settings used to manage regular headers on Silva content.
    """
    grok.provides(IHTTPHeadersSettings)
    grok.implements(IHTTPHeadersSettings)
    grok.context(IPublishable)

    http_disable_cache = False
    http_max_age = 86400
    http_last_modified = True


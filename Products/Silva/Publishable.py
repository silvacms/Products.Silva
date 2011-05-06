# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.SilvaObject import SilvaObject

from five import grok
from silva.core.interfaces.content import IPublishable, INonPublishable


class NonPublishable(SilvaObject):
    """Base content which is not a published content in Silva. It
    doesn't appear in navigation, and is not ordered.
    """
    grok.baseclass()
    grok.implements(INonPublishable)



class Publishable(SilvaObject):
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

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        return True


InitializeClass(Publishable)


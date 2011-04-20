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
from silva.core.interfaces.content import (
    IPublishable, INonPublishable, IVersioning)


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

    # ACCESSORS

    # XXX: those two methods is_published and is_approved are only
    # used in VersionedContent. They should move there.
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_published')
    def is_published(self, update_status=True):
        if IVersioning.providedBy(self):
            return self.is_version_published(update_status=update_status)
        else:
            return 1

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_approved')
    def is_approved(self, update_status=True):
        if IVersioning.providedBy(self):
            return self.is_version_approved(update_status=update_status)
        else:
            # never be approved if there is no versioning
            return 0

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """Analogous to is_deletable() (?)
        """
        return not self.is_published() and not self.is_approved()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_real_container')
    def get_real_container(self):
        """Get the container, even if we're a container.

        If we're the root object, returns None.

        Can be used with acquisition to get the 'nearest' container.
        """
        return self.get_container()


InitializeClass(Publishable)


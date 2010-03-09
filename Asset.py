# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

# Zope 3
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS import SimpleItem
import OFS.interfaces

# Silva
from Products.Silva.SilvaObject import SilvaObject
from Products.Silva import SilvaPermissions
from silva.core import interfaces

logger = logging.getLogger('silva.core')


class Asset(SilvaObject, SimpleItem.SimpleItem):
    grok.baseclass()
    grok.implements(interfaces.IAsset)

    security = ClassSecurityInfo()

    object_type = 'asset'
    _old_size = 0               # Old size of the object.

    # MANIPULATORS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'update_quota')
    def update_quota(self):
        # XXX Should use utility
        service_extension = getattr(self, 'service_extensions', None)
        if not service_extension:
            return
        if not self.service_extensions.get_quota_subsystem_status():
            return

        parent = self.aq_parent
        if not interfaces.IImage.providedBy(parent):
            new_size = self.get_file_size()
            delta = new_size - self._old_size
            parent.update_quota(delta)
            self._old_size = new_size

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'reset_quota')
    def reset_quota(self):
        self._old_size = self.get_file_size()
        return self._old_size

    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_navigation_links')
    def get_navigation_links(self):
        """
        Create a dictionary with top, up, first, previous, next, last links.

        This can be used by Mozilla in the accessibility toolbar.
        """
        return {}

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'version_status')
    def version_status(self):
        return 'public'

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                            'fulltext')
    def fulltext(self):
        fulltextlist = [self.id, self.get_title()]
        return fulltextlist

    def get_filename(self):
        raise NotImplementedError

    def get_file_size(self):
        raise NotImplementedError

    def get_mime_type(self):
        raise NotImplementedError


InitializeClass(Asset)


@grok.subscribe(interfaces.IAsset, OFS.interfaces.IObjectWillBeMovedEvent)
def asset_moved_update_quota(asset, event):
    """Event called on Asset when they are moved to update quota on
    parents folders.
    """

    if asset != event.object:
        return

    if event.newParent is event.oldParent:
        # For rename event, we don't need to do something.
        return

    context = event.newParent or event.oldParent
    if not context.service_extensions.get_quota_subsystem_status():
        return

    try:
        size = asset.get_file_size()
    except (AttributeError, NotImplementedError):
        # Well, not all asset respect its interface.
        path = '/'.join(asset.getPhysicalPath())
        klass = str(asset.__class__)
        logger.error('bad asset object %s - %s' % (path, klass))
        return

    if not size:
        return

    if event.oldParent:
        event.oldParent.update_quota(-size)
    if event.newParent:
        event.newParent.update_quota(size)






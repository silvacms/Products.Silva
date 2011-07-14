# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from five import grok

from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from App.class_init import InitializeClass
from OFS import SimpleItem
import OFS.interfaces

from Products.Silva import SilvaPermissions
from Products.Silva.SilvaObject import ViewableObject
from Products.Silva.Publishable import NonPublishable
from Products.Silva.mangle import Bytes

from silva.core.smi.content import IEditScreen
from silva.core.interfaces import IAsset, IImage
from silva.core.views import views as silvaviews
from silva.core.smi.content.metadata import ContentReferencedBy
from silva.translations import translate as _
from zeam.form import silva as silvaforms

logger = logging.getLogger('silva.core')


class Asset(NonPublishable, ViewableObject, SimpleItem.SimpleItem):
    grok.baseclass()
    grok.implements(IAsset)

    security = ClassSecurityInfo()

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

        parent = aq_parent(self)
        if not IImage.providedBy(parent):
            new_size = self.get_file_size()
            delta = new_size - self._old_size
            if delta:
                parent.update_quota(delta)
                self._old_size = new_size

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'reset_quota')
    def reset_quota(self):
        self._old_size = self.get_file_size()
        return self._old_size

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
        fulltextlist = [self.id, self.get_title()]
        return fulltextlist

    def get_filename(self):
        raise NotImplementedError

    def get_file_size(self):
        raise NotImplementedError

    def get_mime_type(self):
        raise NotImplementedError

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'get_file_system_path')
    def get_file_system_path(self):
        """Return path of the file containing the data on the filesystem.
        """
        return None


InitializeClass(Asset)


@grok.subscribe(IAsset, OFS.interfaces.IObjectWillBeMovedEvent)
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


class AssetEditTab(silvaforms.SMIComposedForm):
    """ Edit tab
    """
    grok.context(IAsset)
    grok.name('content')
    grok.require('silva.ChangeSilvaContent')
    grok.implements(IEditScreen)

    label = _('Edit')


class SMIAssetPortlet(silvaviews.Viewlet):
    grok.baseclass()
    grok.context(IAsset)
    grok.view(AssetEditTab)
    grok.viewletmanager(silvaforms.SMIFormPortlets)


class AssetSize(SMIAssetPortlet):
    """Report size of this asset.
    """
    grok.order(80)

    def update(self):
        self.size = Bytes(self.context.get_file_size())


class AssetPath(SMIAssetPortlet):
    """Give filesystem path to that asset.
    """
    grok.order(90)
    grok.require('zope2.ViewManagementScreens')

    def update(self):
        self.path = None
        path = self.context.get_file_system_path()
        if path is not None:
            self.path = path.replace('/', ' / ')


class AssetReferencedBy(ContentReferencedBy):
    grok.order(100)
    grok.context(IAsset)
    grok.view(AssetEditTab)

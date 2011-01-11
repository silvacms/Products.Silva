# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging
import bisect

# Zope 3
from five import grok
from zope.interface import Interface
from zope import component
from zope.traversing.browser import absoluteURL

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS import SimpleItem
import OFS.interfaces

# Silva
from Products.Silva.Publishable import NonPublishable
from Products.Silva.mangle import Bytes
from Products.Silva import SilvaPermissions

from silva.core.interfaces import IAsset, IImage, IVersion
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import ISilvaURL
from silva.core.smi.interfaces import ISMILayer
from silva.core.references.interfaces import IReferenceService

logger = logging.getLogger('silva.core')


class Asset(NonPublishable, SimpleItem.SimpleItem):
    grok.baseclass()
    grok.implements(IAsset)

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
        if not IImage.providedBy(parent):
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


class SMIAssetMetadata(silvaviews.ViewletManager):
    """Report information on assets.
    """
    grok.context(IAsset)
    grok.view(Interface)


class AssetSize(silvaviews.Viewlet):
    """Report size of this asset.
    """
    grok.context(IAsset)
    grok.layer(ISMILayer)
    grok.order(80)
    grok.viewletmanager(SMIAssetMetadata)

    def update(self):
        self.size = Bytes(self.context.get_file_size())


class AssetPath(silvaviews.Viewlet):
    """Give filesystem path to that asset.
    """
    grok.context(IAsset)
    grok.layer(ISMILayer)
    grok.order(90)
    grok.require('zope2.ViewManagementScreens')
    grok.viewletmanager(SMIAssetMetadata)

    def update(self):
        self.path = None
        path = self.context.get_file_system_path()
        if path is not None:
            self.path = path.replace('/', ' / ')


class AssetReferencedBy(silvaviews.Viewlet):
    """Report usage of this asset
    """
    grok.context(IAsset)
    grok.layer(ISMILayer)
    grok.order(100)
    grok.viewletmanager(SMIAssetMetadata)

    def update(self):
        references = {}
        service = component.getUtility(IReferenceService)
        for reference in service.get_references_to(self.context):
            source = reference.source
            source_versions = []
            if IVersion.providedBy(source):
                source_versions.append(source.id)
                source = source.get_content()

            edit_url = absoluteURL(source, self.request) + '/edit'
            if edit_url in references and source_versions:
                previous_versions = references[edit_url]['versions']
                if previous_versions[-1] > source_versions[0]:
                    bisect.insort_right(previous_versions, source_versions[0])
                    continue
                else:
                    source_versions = previous_versions + source_versions

            source_title = source.get_title_or_id()
            source_url = component.getMultiAdapter(
                (source, self.request), ISilvaURL).preview()
            references[edit_url] = {'title': source_title,
                                    'url': source_url,
                                    'path': '/'.join(source.getPhysicalPath()),
                                    'edit_url': edit_url,
                                    'icon': self.view.get_icon(source),
                                    'versions': source_versions}

        self.references = references.values()
        self.references.sort(key=lambda info: info['title'].lower())

        for info in self.references:
            if info['versions']:
                info['title'] += '(' + ', '.join(info['versions']) + ')'

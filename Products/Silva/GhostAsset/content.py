# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import time

# Zope 3
from five import grok
from zeam.component import component
from zope.interface import noLongerProvides, alsoProvides
from zope.component import getMultiAdapter

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Asset import Asset
from Products.Silva.Ghost import GhostBase
from Products.Silva.Ghost import GhostBaseManipulator, GhostBaseManager

from silva.core.interfaces import IAssetPayload, IGhostManager
from silva.core.interfaces import IGhostAsset, IAsset
from silva.core.interfaces import IImage, IImageIncluable
from silva.core.interfaces.errors import AssetInvalidTarget, ContentError
from silva.core.references.reference import DeleteSourceReferenceValue
from silva.core.references.reference import get_content_from_id, get_content_id
from silva.core.views.interfaces import IContentURL


class ImageDeleteSourceReferenceValue(DeleteSourceReferenceValue):

    def _check_image(self, target):
        source = self.source
        if source is not None:
            is_image = IImage.providedBy(target)
            have_image = IImageIncluable.providedBy(source)
            if is_image and not have_image:
                alsoProvides(source, IImageIncluable)
            elif not is_image and have_image:
                noLongerProvides(source, IImageIncluable)

    def set_target_id(self, target_id):
        self._check_image(get_content_from_id(target_id))
        super(ImageDeleteSourceReferenceValue, self).set_target_id(target_id)

    def set_target(self, target):
        self._check_image(target)
        super(ImageDeleteSourceReferenceValue, self).set_target_id(
            get_content_id(target))


class ImageWeakReferenceValue(ImageDeleteSourceReferenceValue):

    def cleanup(self):
        pass


class GhostAsset(GhostBase, Asset):
    grok.implements(IGhostAsset)
    security = ClassSecurityInfo()
    meta_type = "Silva Ghost Asset"

    def _get_haunted_factories(self, auto_delete=False):
        if auto_delete:
            return ImageDeleteSourceReferenceValue
        return ImageWeakReferenceValue

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_filename')
    def get_filename(self):
        asset = self.get_haunted()
        if asset is not None:
            return asset.get_filename()
        return self.getId()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_file_size')
    def get_file_size(self):
        asset = self.get_haunted()
        if asset is not None:
            return asset.get_file_size()
        return 0

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_mime_type')
    def get_mime_type(self):
        asset = self.get_haunted()
        if asset is not None:
            return asset.get_mime_type()
        return 'application/octet-stream'

    security.declareProtected(
        SilvaPermissions.View, 'get_download_url')
    def get_download_url(self, preview=False, request=None):
        if request is None:
            request = self.REQUEST
        url = getMultiAdapter((self, request), IContentURL).url(preview=preview)
        if preview:
            # In case of preview we add something that change at the
            # end of the url to prevent caching from the browser.
            url += '?' + str(int(time.time()))
        return url

    def get_quota_usage(self):
        # Ghost Assets don't use any quota.
        return -1

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_modification_datetime')
    def get_modification_datetime(self):
        """Return modification datetime.
        """
        asset = self.get_haunted()
        if asset is not None:
            return asset.get_modification_datetime()
        return super(GhostAsset, self).get_modification_datetime()


InitializeClass(GhostAsset)


class GhostAssetManipulator(GhostBaseManipulator):

    def create(self, recursive=False):
        assert self.manager.ghost is None
        factory = self.manager.container.manage_addProduct['Silva']
        try:
            factory.manage_addGhostAsset(self.identifier, None)
        except ValueError as error:
            raise ContentError(error[0], content=self.target)
        ghost = self.manager.container._getOb(self.identifier)
        ghost.set_haunted(self.target, auto_delete=self.manager.auto_delete)
        self.manager.ghost = ghost
        return ghost

    def update(self):
        assert self.manager.ghost is not None
        if IGhostAsset.providedBy(self.manager.ghost):
            self.manager.ghost.set_haunted(
                self.target, auto_delete=self.manager.auto_delete)
        else:
            self.recreate()
        return self.manager.ghost

    def need_update(self):
        if IGhostAsset.providedBy(self.manager.ghost):
            return self.target != self.manager.ghost.get_haunted()
        # Only update if the invalid ghost is an asset.
        return IAsset.providedBy(self.manager.ghost)


@component(IAsset, provides=IGhostManager)
class GhostAssetManager(GhostBaseManager):
    manipulator = GhostAssetManipulator

    def validate(self, target, adding=False):
        error = super(GhostAssetManager, self).validate(target, adding)
        if error is None:
            if not IAsset.providedBy(target):
                return AssetInvalidTarget()
        return error


class GhostAssetPayload(grok.Adapter):
    grok.implements(IAssetPayload)
    grok.context(IGhostAsset)

    def get_payload(self):
        asset = self.context.get_haunted()
        if asset is not None:
            return IAssetPayload(asset).get_payload()
        return None

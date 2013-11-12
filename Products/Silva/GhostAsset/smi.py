# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt


# Zope 3
from five import grok

# Silva
from Products.Silva.Ghost import TargetValidator
from Products.Silva.Asset import AssetEditTab, SMIAssetPortlet

from silva.core.conf.interfaces import IIdentifiedContent
from silva.core.interfaces import IAsset, IGhostAsset, IImageIncluable
from silva.core.references.reference import Reference
from silva.translations import translate as _
from zeam.form import silva as silvaforms


class IGhostAssetSchema(IIdentifiedContent):

    haunted = Reference(IAsset,
            title=_(u"Target"),
            description=_(u"The asset the ghost is mirroring"),
            required=True)


class GhostAssetAddForm(silvaforms.SMIAddForm):
    """ Add form for ghost folders
    """
    grok.name(u'Silva Ghost Asset')

    fields = silvaforms.Fields(IGhostAssetSchema)
    fields['haunted'].referenceNotSetLabel = _(
        u"Click the Lookup button to select an asset to haunt.")
    dataValidators = [TargetValidator('haunted', IAsset, adding=True)]

    def _add(self, parent, data):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addGhostAsset(
            data['id'], None, haunted=data['haunted'])


class GhostAssetEditForm(silvaforms.SMISubForm):
    """ Edit form Ghost Folder
    """
    grok.context(IGhostAsset)
    grok.view(AssetEditTab)
    grok.order(10)

    label = _(u'Edit ghost')
    ignoreContent = False
    dataManager = silvaforms.SilvaDataManager
    dataValidators = [TargetValidator('haunted', IAsset, adding=False)]
    fields = silvaforms.Fields(IGhostAssetSchema).omit('id')
    actions  = silvaforms.Actions(
        silvaforms.CancelEditAction(),
        silvaforms.EditAction())


class GhostAssetPortlet(SMIAssetPortlet):
    grok.context(IGhostAsset)
    grok.order(10)

    def update(self):
        self.is_image = IImageIncluable.providedBy(self.context)
        self.filename = self.context.get_filename()
        self.mime_type = self.context.get_mime_type()
        self.download_url = self.context.get_download_url(
            preview=True, request=self.request)

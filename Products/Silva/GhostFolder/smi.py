# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt


# Zope 3
from five import grok

# Zope 2
from AccessControl.security import checkPermission

# Silva
from Products.Silva.Ghost import TargetValidator

from silva.core.conf.interfaces import IIdentifiedContent
from silva.core.references.reference import Reference
from silva.core.interfaces import IContainer, IGhostFolder
from silva.core.interfaces.errors import ContentError
from silva.ui.menu import ContentMenu, MenuItem
from silva.translations import translate as _
from zeam.form import silva as silvaforms


class IGhostFolderSchema(IIdentifiedContent):

    haunted = Reference(IContainer,
            title=_(u"Target"),
            description=_(u"The internal folder the ghost is mirroring"),
            required=True)


class SyncAction(silvaforms.Action):
    description = _(u"Synchronize target and ghost folder content")
    ignoreRequest = True

    def available(self, form):
        return checkPermission('silva.ChangeSilvaContent', form.context)

    def __call__(self, form):
        folder = form.context
        if folder.get_link_status() is not None:
            form.send_message(
                _(u'Ghost Folder was not synchronized, '
                  u'because the target is invalid.'),
                type='error')
            return silvaforms.FAILURE
        try:
            folder.haunt()
        except ContentError as error:
            form.send_message(
                error.reason,
                type='error')
            return silvaforms.FAILURE
        else:
            form.send_message(
                _(u'Ghost Folder synchronized.'), type='feedback')
            return silvaforms.SUCCESS


class GhostFolderAddForm(silvaforms.SMIAddForm):
    """ Add form for ghost folders
    """
    grok.name(u'Silva Ghost Folder')

    fields = silvaforms.Fields(IGhostFolderSchema)
    fields['haunted'].referenceNotSetLabel = _(
        u"Click the Lookup button to select a container to haunt.")
    dataValidators = [TargetValidator('haunted', IContainer, adding=True)]

    def _add(self, parent, data):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addGhostFolder(
            data['id'], None, haunted=data['haunted'])


class GhostFolderEditForm(silvaforms.SMIEditForm):
    """ Edit form Ghost Folder
    """
    grok.context(IGhostFolder)
    grok.name('edit')

    fields = silvaforms.Fields(IGhostFolderSchema).omit('id')
    dataValidators = [TargetValidator('haunted', IContainer, adding=False)]
    actions = silvaforms.SMIEditForm.actions + SyncAction(_(u'Synchronize'))


class GhostFolderEditMenu(MenuItem):
    grok.adapts(ContentMenu, IGhostFolder)
    grok.order(10.1)            # Goes right after the content tab.
    name = _(u'Edit')
    screen = GhostFolderEditForm

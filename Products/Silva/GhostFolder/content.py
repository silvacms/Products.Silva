# -*- coding: utf-8 -*-
# Copyright (c) 2003-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from zeam.component import component, getComponent
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from App.class_init import InitializeClass
from OFS.interfaces import IObjectClonedEvent

# silva
from Products.Silva import SilvaPermissions, helpers
from Products.Silva.Folder import Folder
from Products.Silva.Ghost import GhostBase
from Products.Silva.Ghost import GhostBaseManipulator, GhostBaseManager
from Products.Silva.Publication import Publication
from Products.SilvaMetadata.interfaces import IMetadataService

from silva.core import conf as silvaconf
from silva.core.interfaces import IContainer, IGhostFolder, IGhostManager
from silva.core.interfaces import IPublication
from silva.core.interfaces.errors import ContainerInvalidTarget
from silva.core.interfaces.errors import ContentError, ContentErrorBundle
from silva.translations import translate as _


class CopyManipulator(GhostBaseManipulator):

    def make_copy(self):
        ghost = self.target._getCopy(self.manager.container)
        self.manager.container._setObject(self.identifier, ghost)
        # Publish if needed ?
        return self.manager.container._getOb(self.identifier)

    def create(self, recursive=False):
        assert self.manager.ghost is None
        ghost = self.make_copy()
        self.manager.ghost = ghost
        return ghost

    def update(self):
        assert self.manager.ghost is not None
        self.manager.container.manage_delObjects([self.identifier])
        ghost = self.make_copy()
        self.manager.ghost = ghost
        return ghost

    def need_update(self):
        return True


class CopyManager(GhostBaseManager):
    manipulator = CopyManipulator


def get_factory(target):
    return getComponent((target,), IGhostManager, default=CopyManager)


class GhostFolder(GhostBase, Folder):
    __doc__ = _("""Ghost Folders are similar to Ghosts, but instead of being a
       placeholder for a document, they create placeholders and/or copies of all
       the contents of the &#8216;original&#8217; folder. The advantage of Ghost
       Folders is the contents stay in sync with the original, by manual or
       automatic resyncing. Note that when a folder is
       ghosted, assets &#8211; such as Images and Files &#8211; are copied
       (physically duplicated) while documents are ghosted.""")

    meta_type = 'Silva Ghost Folder'

    grok.implements(IGhostFolder)
    silvaconf.icon('icons/ghost_folder.png')
    silvaconf.priority(0)

    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'haunt')
    def haunt(self):
        """populate the the ghost folder with ghosts
        """
        haunted = self.get_haunted()
        if haunted is None:
            return False
        stack = self._haunt_diff(haunted, self)
        errors = []

        while stack:
            # breadth first search
            h_container, h_id, g_container, g_id = stack.pop(0)

            if h_id is None:
                # object was removed from haunted, so just remove it and
                # continue
                g_container.manage_delObjects([g_id])
                continue

            h_ob = h_container._getOb(h_id)
            g_ob = None
            if g_id is not None:
                g_ob = g_container._getOb(g_id)

            try:
                g_ob = get_factory(h_ob)(
                    ghost=g_ob,
                    container=g_container,
                    auto_delete=True,
                    auto_publish=True).modify(h_ob, h_id).verify()
            except ContentError as error:
                errors.append(error)

            if IContainer.providedBy(h_ob) and g_ob is not None:
                stack.extend(self._haunt_diff(h_ob, g_ob))

        if errors:
            raise ContentErrorBundle(
                _(u"Error while synchronizing the Ghost Folder: "
                  u"not all its content have been updated properly."),
                content=self, errors=errors)
        return True

    def _haunt_diff(self, haunted, ghost):
        """diffes two containers

            haunted: IContainer, container to be haunted
            ghost: IContainer, ghost

            returns list of tuple:
            [(haunted, h_id, ghost, g_id)]
            whereby
                h_id is the haunted object's id or None if a ghost exists but
                    no object to be haunted
                g_id is the ghost's id or None if the ghost doesn't exist but
                    has to be created
                haunted and ghost are the objects passed in
        """
        assert IContainer.providedBy(haunted)
        assert IContainer.providedBy(ghost)
        h_ids = list(haunted.objectIds())
        g_ids = list(ghost.objectIds())
        h_ids.sort()
        g_ids.sort()
        ids = []
        while h_ids or g_ids:
            h_id = None
            g_id = None
            if h_ids:
                h_id = h_ids[0]
            if g_ids:
                g_id = g_ids[0]
            if h_id == g_id or h_id is None or g_id is None:
                ids.append((h_id, g_id))
                if h_ids:
                    del h_ids[0]
                if g_ids:
                    del g_ids[0]
            elif h_id < g_id:
                ids.append((h_id, None))
                del h_ids[0]
            elif h_id > g_id:
                ids.append((None, g_id))
                del g_ids[0]
        return [(haunted, h_id, ghost, g_id) for (h_id, g_id) in ids]

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'to_publication')
    def to_publication(self):
        """replace self with a folder"""
        haunted = self.get_haunted()
        if haunted is not None:
            binding = getUtility(IMetadataService).getMetadata(haunted)
            data_content = binding.get('silva-content', acquire=0)
            data_extra = binding.get('silva-extra', acquire=0)
        helpers.convert_content(self, Publication)
        if haunted is not None:
            binding = getUtility(IMetadataService).getMetadata(self)
            binding.setValues('silva-content', data_content)
            binding.setValues('silva-extra', data_extra)

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'to_folder')
    def to_folder(self):
        """replace self with a folder"""
        haunted = self.get_haunted()
        if haunted is not None:
            binding = getUtility(IMetadataService).getMetadata(haunted)
            data_content = binding.get('silva-content', acquire=0)
            data_extra = binding.get('silva-extra', acquire=0)
        helpers.convert_content(self, Folder)
        if haunted is not None:
            binding = getUtility(IMetadataService).getMetadata(self)
            binding.setValues('silva-content', data_content)
            binding.setValues('silva-extra', data_extra)

    security.declareProtected(SilvaPermissions.View,'get_publication')
    def get_publication(self):
        """returns self if haunted object is a publication"""
        content = self.get_haunted()
        if IPublication.providedBy(content):
            return self.aq_inner
        return aq_parent(self).get_publication()

    def is_transparent(self):
        """show in subtree? depends on haunted object"""
        content = self.get_haunted()
        if IContainer.providedBy(content):
            return content.is_transparent()
        return 0

    def is_deletable(self):
        pass


InitializeClass(GhostFolder)


class GhostFolderManipulator(GhostBaseManipulator):

    def create(self, recursive=False):
        assert self.manager.ghost is None
        factory = self.manager.container.manage_addProduct['Silva']
        try:
            factory.manage_addGhostFolder(self.identifier, None)
        except ValueError as error:
            raise ContentError(error[0], content=self.target)
        ghost = self.manager.container._getOb(self.identifier)
        ghost.set_haunted(self.target, auto_delete=self.manager.auto_delete)
        if recursive:
            ghost.haunt()
        self.manager.ghost = ghost
        return ghost

    def update(self):
        assert self.manager.ghost is not None
        if IGhostFolder.providedBy(self.manager.ghost):
            self.manager.ghost.set_haunted(
                self.target, auto_delete=self.manager.auto_delete)
        else:
            self.recreate()

    def need_update(self):
        if IGhostFolder.providedBy(self.manager.ghost):
            return self.target != self.manager.ghost.get_haunted()
        # Only update if the invalid ghost is an asset.
        return IContainer.providedBy(self.manager.ghost)


@component(IContainer, provides=IGhostManager)
class GhostFolderManager(GhostBaseManager):
    manipulator = GhostFolderManipulator

    def validate(self, target, adding=False):
        error = super(GhostFolderManager, self).validate(target, adding)
        if error is None:
            if not IContainer.providedBy(target):
                return ContainerInvalidTarget()
        return error


@grok.subscribe(IGhostFolder, IObjectCreatedEvent)
@grok.subscribe(IGhostFolder, IObjectClonedEvent)
def haunt_created_folder(folder, event):
    if (folder != event.object or
        IObjectCopiedEvent.providedBy(event)):
        return
    # If the ghost folder is in a valid state after creation or copy,
    # haunt its content.
    if folder.get_link_status() is None:
        folder.haunt()


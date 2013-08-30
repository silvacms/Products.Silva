# -*- coding: utf-8 -*-
# Copyright (c) 2003-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent

# Zope 2
from AccessControl import ClassSecurityInfo
from AccessControl.security import checkPermission
from Acquisition import aq_parent
from App.class_init import InitializeClass
from OFS.interfaces import IObjectClonedEvent

# silva
from Products.Silva.Folder import Folder
from Products.Silva.Publication import Publication
from Products.Silva import SilvaPermissions, helpers
from Products.Silva.Ghost import GhostBase
from Products.Silva.Ghost import TargetValidator
from Products.SilvaMetadata.interfaces import IMetadataService

from silva.core import conf as silvaconf
from silva.core.interfaces import IAddableContents
from silva.core.interfaces import IOrderManager, IPublicationWorkflow
from silva.core.interfaces import (
    IContainer, IContent, IGhost,
    IPublication, IGhostFolder)
from silva.core.conf.interfaces import IIdentifiedContent
from silva.core.references.reference import Reference
from silva.ui.menu import ContentMenu, MenuItem
from silva.translations import translate as _

from zeam.form import silva as silvaforms


class Sync(object):

    def __init__(self, target_container, target, ghost_container, ghost):
        self.target_container = target_container
        self.target = target
        self.ghost_container = ghost_container
        self.ghost = ghost

        self.target_id = target.getId()
        if ghost is not None:
            self.ghost_id = ghost.getId()

    def get_real_target(self):
        return self.target

    def update(self):
        raise NotImplementedError

    def verify(self):
        return True

    def create(self):
        raise NotImplementedError

    finish = None


class SyncContainer(Sync):

    def create(self):
        target = self.get_real_target()
        if target is not None:
            factory = self.ghost_container.manage_addProduct['Silva']
            factory.manage_addGhostFolder(self.target_id, None)
            self.ghost = self.ghost_container._getOb(self.target_id)
            self.ghost.set_haunted(target, auto_delete=True)
        return self.ghost

    def verify(self):
        return self.get_real_target() == self.ghost.get_haunted()

    def update(self):
        self.ghost.set_haunted(self.get_real_target(), auto_delete=True)
        return self.ghost

    def finish(self):
        ## XXX: I don't think that works (like ever worked)
        target = self.get_real_target()
        if target is not None:
            orderer = IOrderManager(self.ghost)
            for index, content in enumerate(target.get_ordered_publishables()):
                orderer.move(content, index)


class SyncGhostContainer(SyncContainer):

    def get_real_target(self):
        return self.target.get_haunted()


class SyncContent(Sync):

    def create(self):
        target = self.get_real_target()
        if target is not None:
            factory = self.ghost_container.manage_addProduct['Silva']
            factory.manage_addGhost(self.target_id, None)
            self.ghost = self.ghost_container._getOb(self.target_id)
            version = self.ghost.get_editable()
            version.set_haunted(self.get_real_target(), auto_delete=True)
            IPublicationWorkflow(self.ghost).publish()
        return self.ghost

    def verify(self):
        return self.get_real_target() == self.ghost.get_haunted()

    def update(self):
        publication = IPublicationWorkflow(self.ghost)
        if self.ghost.get_editable() is None:
            publication.new_version()
        version = self.ghost.get_editable()
        version.set_haunted(self.get_real_target(), auto_delete=True)
        publication.publish()
        return self.ghost


class SyncGhost(SyncContent):

    def get_real_target(self):
        return self.target.get_haunted()


class SyncCopy(Sync):
    # this is anything else -- copy it. We cannot check if it was
    # modified and if copying is really necessary.

    def create(self):
        ghost = self.target._getCopy(self.ghost_container)
        self.ghost_container._setObject(self.target_id, ghost)
        return self.ghost_container._getOb(self.target_id)

    def update(self):
        assert self.ghost is not None
        self.ghost_container.manage_delObjects([self.target_id])
        return self.create()




# sync map... (haunted objects interface, ghost objects interface,
# update/create class) order is important, i.e. interfaces are
# checked in this order.
SYNC_MAP = [
    (IGhostFolder, IGhostFolder, SyncGhostContainer),
    (IContainer, IContainer, SyncContainer),
    (IGhost, IGhost, SyncGhost),
    (IContent, IGhost, SyncContent),
    (None, None, SyncCopy),
    ]


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
            return
        stack = self._haunt_diff(haunted, self)
        updaters = [SyncContainer(None, haunted, None, self)]

        while stack:
            # breadth first search
            h_container, h_id, g_container, g_id = stack.pop(0)
            if h_id is None:
                # object was removed from haunted, so just remove it and
                # continue
                g_container.manage_delObjects([g_id])
                continue
            h_ob = h_container._getOb(h_id)

            if g_id is None:
                # object was added to haunted
                g_ob = None
            else:
                # object is there but may have changed
                g_ob = g_container._getOb(g_id)
            g_ob_new = None

            for h_if, g_if, factory in SYNC_MAP:
                if h_if and not h_if.providedBy(h_ob):
                    continue
                if g_ob is None:
                    # matching haunted interface, no ghost -> create
                    updater = factory(h_container, h_ob, g_container, g_ob)
                    g_ob_new = updater.create()
                    if updater.finish is not None:
                        updaters.append(updater)
                    break
                if g_if and not g_if.providedBy(g_ob):
                    # haunted interface machces but ghost interface doesn't
                    continue
                # haunted interface and ghost interface match -> update
                updater = factory(h_container, h_ob, g_container, g_ob)
                # if the object is not uptodate, update it
                if not updater.verify():
                    g_ob_new = updater.update()
                    if updater.finish is not None:
                        updaters.append(updater)
                else:
                    g_ob_new = g_ob
                break
            else:
                assert True, "no updater was called for %r" % (
                    (h_container, h_ob, g_container, g_ob),)
            if IContainer.providedBy(h_ob) and g_ob_new is not None:
                stack.extend(self._haunt_diff(h_ob, g_ob_new))
        for updater in updaters:
            updater.finish()

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

    # all this is for a nice side bar
    def is_transparent(self):
        """show in subtree? depends on haunted object"""
        content = self.get_haunted()
        if IContainer.providedBy(content):
            return content.is_transparent()
        return 0

    security.declareProtected(SilvaPermissions.View,'get_publication')
    def get_publication(self):
        """returns self if haunted object is a publication"""
        content = self.get_haunted()
        if IPublication.providedBy(content):
            return self.aq_inner
        return aq_parent(self).get_publication()

    def is_deletable(self):
        pass


InitializeClass(GhostFolder)


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
        if folder.get_link_status() is None:
            folder.haunt()
            form.send_message(
                _(u'Ghost Folder synchronized.'), type='feedback')
            return silvaforms.SUCCESS
        form.send_message(
            _(u'Ghost Folder was not synchronized, because the target is invalid.'),
            type='error')
        return silvaforms.FAILURE


class GhostFolderAddForm(silvaforms.SMIAddForm):
    """ Add form for ghost folders
    """
    grok.name(u'Silva Ghost Folder')

    fields = silvaforms.Fields(IGhostFolderSchema)
    fields['haunted'].referenceNotSetLabel = _(
        u"Click the Lookup button to select a container to haunt.")
    dataValidators = [
        TargetValidator('haunted', is_folderish=True, adding=True)]

    def _add(self, parent, data):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addGhostFolder(
            data['id'], None, haunted=data['haunted'])


class GhostFolderEditForm(silvaforms.SMIEditForm):
    """ Edit form Ghost Folder
    """
    grok.context(IGhostFolder)
    grok.name('silva.ui.edit')

    fields = silvaforms.Fields(IGhostFolderSchema).omit('id')
    dataValidators = [
        TargetValidator('haunted', is_folderish=True, adding=False)]
    actions = silvaforms.SMIEditForm.actions + SyncAction(_(u'Synchronize'))


class GhostFolderEditMenu(MenuItem):
    grok.adapts(ContentMenu, IGhostFolder)
    grok.order(10.1)            # Goes right after the content tab.
    name = _(u'Edit')
    screen = GhostFolderEditForm


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


class AddableContents(grok.Adapter):
    grok.context(IGhostFolder)
    grok.implements(IAddableContents)
    grok.provides(IAddableContents)

    def get_authorized_addables(self):
        return []

    def get_container_addables(self):
        return []

    def get_all_addables(self):
        return []


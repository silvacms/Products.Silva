# -*- coding: utf-8 -*-
# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from zope.annotation.interfaces import IAnnotations
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from App.class_init import InitializeClass
from DateTime import DateTime

# silva
from Products.Silva import Folder
from Products.Silva import SilvaPermissions
from Products.Silva.Ghost import GhostBase, GhostEditForm

from silva.core import conf as silvaconf
from silva.core.interfaces import IAddableContents
from silva.core.interfaces import IOrderManager
from silva.core.interfaces import (
    IContainer, IContent, IGhost, IVersionedContent,
    IPublication, IGhostFolder, IGhostAware)
from silva.core.conf.interfaces import IIdentifiedContent
from silva.core.references.reference import Reference
from silva.ui.menu import ContentMenu, MenuItem
from silva.translations import translate as _

from zeam.form import silva as silvaforms


class Sync(object):

    def __init__(self, gf, h_container, h_ob, g_container, g_ob):
        self.h_container = h_container
        self.h_ob = h_ob
        self.g_container = g_container
        self.g_ob = g_ob

        self.h_id = h_ob.getId()
        if g_ob is not None:
            self.g_id = g_ob.getId()

    def update(self):
        self._do_update()
        return self.g_container._getOb(self.h_id)

    def create(self):
        self._do_create()
        return self.g_container._getOb(self.h_id)

    def finish(self):
        pass

    def _do_update(self):
        raise NotImplementedError

    def _do_create(self):
        raise NotImplementedError


class SyncContainer(Sync):

    def finish(self):
        ## XXX: I don't think that works (like ever worked)
        orderer = IOrderManager(self.g_ob)
        for index, content in enumerate(self.h_ob.get_ordered_publishables()):
            orderer.move(content, index)

    def _do_create(self):
        self.g_container.manage_addProduct['Silva'].manage_addGhostFolder(
            self.h_id, 'Ghost Folder', haunted=self.h_ob)
        self.g_ob = self.g_container._getOb(self.h_id)
        self._do_update()

    def _do_update(self):
        pass


class SyncGhost(Sync):

    def _do_update(self):
        content = self._get_content()
        old_content = self.g_ob.get_haunted()
        if content == old_content:
            return
        self.g_ob.create_copy()
        version_id = self.g_ob.get_unapproved_version()
        version = getattr(self.g_ob, version_id)
        version.set_haunted(content)

    def _do_create(self):
        content = self._get_content()
        self.g_container.manage_addProduct['Silva'].manage_addGhost(
            self.h_id, 'Ghost', haunted=content)

    def _get_content(self):
        return  self.h_ob.get_haunted()


class SyncContent(SyncGhost):

    def _get_content(self):
        return self.h_ob


class SyncCopy(Sync):
    # this is anything else -- copy it. We cannot check if it was
    # modified and if copying is really necessary.

    def _do_update(self):
        assert self.g_ob is not None
        self.g_container.manage_delObjects([self.h_id])
        self.create()

    def _do_create(self):
        g_ob_new = self.h_ob._getCopy(self.g_container)
        self.g_container._setObject(self.h_id, g_ob_new)


class GhostFolder(GhostBase, Folder.Folder):
    __doc__ = _("""Ghost Folders are similar to Ghosts, but instead of being a
       placeholder for a document, they create placeholders and/or copies of all
       the contents of the &#8216;original&#8217; folder. The advantage of Ghost
       Folders is the contents stay in sync with the original, by manual or
       automatic resyncing. Note that when a folder is
       ghosted, assets &#8211; such as Images and Files &#8211; are copied
       (physically duplicated) while documents are ghosted.""")

    meta_type = 'Silva Ghost Folder'

    grok.implements(IGhostFolder)
    silvaconf.icon('icons/silvaghost_folder.gif')
    silvaconf.priority(0)

    security = ClassSecurityInfo()

    # sync map... (haunted objects interface, ghost objects interface,
    # update/create class) order is important, i.e. interfaces are
    # checked in this order.
    _sync_map = [
        (IContainer, IContainer, SyncContainer),
        (IGhost, IGhost, SyncGhost),
        (IContent, IGhost, SyncContent),
        (None, None, SyncCopy),
        ]


    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'haunt')
    def haunt(self):
        """populate the the ghost folder with ghosts
        """
        haunted = self.get_haunted()
        if haunted is None:
            return
        if self.get_link_status() != self.LINK_OK:
            return
        ghost = self
        assert IContainer.providedBy(haunted)
        object_list = self._haunt_diff(haunted, ghost)
        upd = SyncContainer(self, None, haunted, None, self)
        updaters = [upd]

        while object_list:
            # breadth first search
            h_container, h_id, g_container, g_id = object_list[0]
            del(object_list[0])
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

            for h_if, g_if, update_class in self._sync_map:
                if h_if and not h_if.providedBy(h_ob):
                    continue
                if g_ob is None:
                    # matching haunted interface, no ghost -> create
                    uc = update_class(self, h_container, h_ob,
                        g_container, g_ob)
                    updaters.append(uc)
                    g_ob_new = uc.create()
                    break
                if g_if and not g_if.providedBy(g_ob):
                    # haunted interface machces but ghost interface doesn't
                    continue
                # haunted interface and ghost interface match -> update
                uc = update_class(self, h_container, h_ob, g_container,
                    g_ob)
                updaters.append(uc)
                g_ob_new = uc.update()
                break

            msg = "no updater was called for %r" % ((self, h_container, h_ob, g_container, g_ob), )
            assert g_ob_new is not None, msg
            if IContainer.providedBy(h_ob):
                object_list.extend(self._haunt_diff(h_ob, g_ob_new))
        for updater in updaters:
            updater.finish()

        self._publish_ghosts()

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

    security.declareProtected(SilvaPermissions.View,'get_link_status')
    def get_link_status(self):
        """return an error code if this version of the ghost is broken.
        returning None means the ghost is Ok.
        """
        content = self.get_haunted()
        if content is None:
            return self.LINK_VOID
        if IGhostAware.providedBy(content):
            return self.LINK_GHOST
        if IContent.providedBy(content):
            return self.LINK_CONTENT
        if not IContainer.providedBy(content):
            return self.LINK_NO_FOLDER
        if self.isReferencingSelf(content):
            return self.LINK_CIRC
        return self.LINK_OK

    def isReferencingSelf(self, content):
        """returns True if ghost folder references self or a ancestor of self
        """
        if content is None:
            content = self.get_haunted()
            if content is None:
                # if we're not referencing anything it is not a circular
                # reference for sure
                return False
        content_path = content.getPhysicalPath()
        self_path = self.getPhysicalPath()
        return content_path == self_path[:len(content_path)]

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'to_publication')
    def to_publication(self):
        """replace self with a folder"""
        new_self = self._to_folder_or_publication_helper(to_folder=0)
        self._copy_annotations_from_haunted(new_self)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'to_folder')
    def to_folder(self):
        """replace self with a folder"""
        new_self = self._to_folder_or_publication_helper(to_folder=1)
        self._copy_annotations_from_haunted(new_self)

    def _copy_annotations_from_haunted(self, new_self):
        src = IAnnotations(self.get_haunted())
        dst = IAnnotations(new_self)
        for key in src.keys():
            dst[key] = src[key]

    # all this is for a nice side bar
    def is_transparent(self):
        """show in subtree? depends on haunted object"""
        content = self.get_haunted()
        if IContainer.providedBy(content):
            return content.is_transparent()
        return 0

    def get_publication(self):
        """returns self if haunted object is a publication"""
        content = self.get_haunted()
        if IPublication.providedBy(content):
            return self.aq_inner
        return self.aq_inner.aq_parent.get_publication()

    def is_deletable(self):
        return 1

    def _publish_ghosts(self):
        activate_list = self.objectValues()
        # ativate all containing objects, depth first
        while activate_list:
            object = activate_list.pop()
            if IContainer.providedBy(object):
                activate_list += object.objectValues()
            if IVersionedContent.providedBy(object):
                if object.is_published():
                    continue
                if not object.get_unapproved_version():
                    object.create_copy()
                object.set_unapproved_version_publication_datetime(
                    DateTime())
                object.approve_version()


InitializeClass(GhostFolder)


class IGhostFolderSchema(IIdentifiedContent):
    haunted = Reference(IContainer,
            title=_(u"target"),
            description=_(u"The silva object the ghost is mirroring"),
            required=True)


class SyncAction(silvaforms.Action):
    description = _(u"Synchronize target and ghost folder content")
    ignoreRequest = True

    def __call__(self, form):
        folder = form.context
        if folder.get_link_status() == folder.LINK_OK:
            folder.haunt()
            form.send_message(
                _(u'Ghost Folder synchronized'), type='feedback')
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

    def _add(self, parent, data):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addGhostFolder(
            data['id'], 'Ghost', haunted=data['haunted'])



class AccessMenu(MenuItem):
    grok.adapts(ContentMenu, IGhostFolder)
    grok.order(15)
    name = _(u'Edit')
    screen = 'edit'


class GhostFolderEditForm(GhostEditForm):
    """ Edit form Ghost Folder
    """
    grok.context(IGhostFolder)
    grok.name('silva.ui.edit')

    fields = silvaforms.Fields(IGhostFolderSchema).omit('id')
    actions = GhostEditForm.actions + SyncAction(_(u'Synchronize'))


@grok.subscribe(IGhostFolder, IObjectCreatedEvent)
def haunt_created_folder(folder, event):
    aq_inner(folder).haunt()


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


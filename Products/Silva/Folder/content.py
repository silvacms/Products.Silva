# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.container.contained import notifyContainerModified
from zope.event import notify
from zope.lifecycleevent import ObjectRemovedEvent
from zope.traversing.browser import absoluteURL

# Zope
from AccessControl import ClassSecurityInfo, getSecurityManager
from App.class_init import InitializeClass
from OFS.Folder import Folder as BaseFolder
from OFS.Uninstalled import BrokenClass
from OFS.event import ObjectWillBeRemovedEvent
from OFS.subscribers import compatibilityCall
import OFS.interfaces

# Silva
from Products.Silva.ExtensionRegistry import meta_types_for_interface
from Products.Silva.SilvaObject import SilvaObject
from Products.Silva.Publishable import Publishable
from Products.Silva import SilvaPermissions
from Products.Silva import helpers

from silva.core.interfaces import (
    IContentImporter, IPublishable, IContent,
    INonPublishable, IContainer, IFolder, IRoot)

from silva.core import conf as silvaconf
from silva.translations import translate as _


class Folder(SilvaObject, Publishable, BaseFolder):
    __doc__ = _("""The presentation of the information within a
       publication is structured with folders. They determine the visual
       hierarchy that a Visitor sees. Folders on the top level
       define sections of a publication, subfolders define chapters, etc.
       Note that unlike publications, folders are transparent, meaning you
       can see through them in the sidebar tree navigation and the Publish
       screen.
    """)
    security = ClassSecurityInfo()

    meta_type = "Silva Folder"
    object_type = 'container'

    grok.implements(IFolder)
    silvaconf.icon('www/silvafolder.gif')
    silvaconf.priority(-5)

    @property
    def manage_options(self):
        # A hackish way to get a Silva tab in between the standard ZMI tabs
        manage_options = (BaseFolder.manage_options[0], )
        return manage_options + \
            ({'label':'Silva /edit...', 'action':'edit'}, ) + \
            BaseFolder.manage_options[1:]

    _allow_feeds = False
    used_space = 0

    def __init__(self, id):
        super(Folder, self).__init__(id)
        self._ordered_ids = []
        self._addables_allowed_in_container = None

    # override ObjectManager implementation, so that additional filtering
    # can be done to remove those objects that aren't zmi-addable
    def filtered_meta_types(self, user=None):
        mt = Folder.inheritedAttribute('filtered_meta_types')(self, user)
        newm = []
        for m in mt:
            cf = m['container_filter']
            #If the container_filter is the special filter for
            #Silva content types, then call it to see if that type
            #should be filtered from the zmi-add list as well
            if cf and cf.__name__ == "SilvaZMIFilter" \
                   and not cf(self, filter_addable=True):
                continue
            newm.append(m)
        return newm

    # override ObjectManager implementaton to trigger all events
    # before deleting content / after deleting all content.
    def manage_delObjects(self, ids=[], REQUEST=None):
        """Delete objects.
        """
        if isinstance(ids, basestring):
            ids = [ids]

        try:
            protected = self._reserved_names
        except:
            protected = ()

        deleted_objects = []
        for identifier in ids:
            if identifier in protected:
                continue
            ob = self._getOb(identifier, None)
            if ob is None:
                continue
            deleted_objects.append((identifier, ob))

        for identifier, ob in deleted_objects:
            compatibilityCall('manage_beforeDelete', ob, ob, self)
            notify(ObjectWillBeRemovedEvent(ob, self, identifier))

        for identifier, ob in deleted_objects:
            self._objects = tuple([i for i in self._objects if i['id'] != identifier])
            self._delOb(identifier)
            try:
                ob._v__object_deleted__ = 1
            except:
                pass

        for identifier, ob in deleted_objects:
            notify(ObjectRemovedEvent(ob, self, identifier))

        if deleted_objects:
            notifyContainerModified(self)

        if REQUEST is not None:
            # For ZMI
            REQUEST.RESPONSE.redirect(
                absoluteURL(self, REQUEST) + '/manage_main')

    # MANIPULATORS

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'move_object_up')
    def move_object_up(self, id):
        """Move object up. Returns true if move succeeded.
        """
        ids = self._ordered_ids
        try:
            i = ids.index(id)
        except ValueError:
            return 0
        if i == 0:
            return 0
        ids[i], ids[i - 1] = ids[i - 1], ids[i]
        self._ordered_ids = ids
        return 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'move_object_down')
    def move_object_down(self, id):
        """move object down.
        """
        ids = self._ordered_ids
        try:
            i = ids.index(id)
        except ValueError:
            return 0
        if i == len(ids) - 1:
            return 0
        ids[i], ids[i + 1] = ids[i + 1], ids[i]
        self._ordered_ids = ids
        return 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'move_to')
    def move_to(self, move_ids, index):
        ids = self._ordered_ids
        # check whether all move_ids are known
        for move_id in move_ids:
            if move_id not in ids:
                return 0
        for id in move_ids:
            if ids.index(id) < index:
                index += 1
                break
        ids_without_moving_ids = []
        move_ids_in_order = []
        for id in ids:
            if id in move_ids:
                move_ids_in_order.append(id)
                ids_without_moving_ids.append(None)
            else:
                ids_without_moving_ids.append(id)
        ids = ids_without_moving_ids
        move_ids = move_ids_in_order
        move_ids.reverse()
        for move_id in move_ids:
            ids.insert(index, move_id)
        ids = [id for id in ids if id is not None]
        self._ordered_ids = ids
        return 1

    def _add_ordered_id(self, item):
        """Add item to the end of the list of ordered ids.
        """
        # this already happens to do what we want
        # this works in case of active objects that were added
        # (they're added to the list of ordered ids)
        # and also for inactive objects
        # (they're not added to the list; nothing happens)
        if not IPublishable.providedBy(item):
            return
        if IContent.providedBy(item) and item.is_default():
            return
        ids = self._ordered_ids
        id = item.id
        if id not in ids:
            ids.append(id)
            self._ordered_ids = ids
            self._p_changed = 1

    def _remove_ordered_id(self, item):
        if not IPublishable.providedBy(item):
            return
        if IContent.providedBy(item) and item.is_default():
            return
        ids = self._ordered_ids
        if item.id in ids:
            ids.remove(item.id)
            self._ordered_ids = ids
            self._p_changed = 1

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'refresh_active_publishables')
    def refresh_active_publishables(self):
        """Clean up all ordered ids in this container and all subcontainers.
        This method normally does not need to be called, but if something is
        wrong, this can be called in emergency situations. WARNING: all
        ordering information is lost!
        """
        ids = []
        for object in self.objectValues():
            if not IPublishable.providedBy(object):
                continue
            if IContent.providedBy(object) and object.is_default():
                continue
            ids.append(object.id)
            if IContainer.providedBy(object):
                object.refresh_active_publishables()
        self._ordered_ids = ids

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_allow_feeds')
    def set_allow_feeds(self, allow):
        """change the flag that indicates whether rss/atom feeds are allowed
        on this container"""
        self._allow_feeds = allow

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_publication')
    def to_publication(self):
        """Turn this folder into a publication.
        """
        self._to_folder_or_publication_helper(to_folder=0)

    def _to_folder_or_publication_helper(self, to_folder):
        if to_folder:
            sc = helpers.SwitchClass(Folder)
        else:
            # to publication
            from Products.Silva.Publication import Publication
            sc = helpers.SwitchClass(Publication)
        return sc.upgrade(self)


    def _verify_quota(self):
        # Hook to check quota. Do nothing by default.
        pass

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'update_quota')
    def update_quota(self, delta):

        if IContentImporter.providedBy(self.aq_parent):
            self.aq_inner.update_quota(delta)
            return

        self.used_space += delta
        if delta > 0:           # If we add stuff, check we're not
                                # over quota.
            self._verify_quota()

        if not IRoot.providedBy(self):
            self.aq_parent.update_quota(delta)


    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """Check to see if the title can be set by user, meaning:
        * he is Editor/ChiefEditor/Manager, or
        * he is Author _and_ the Folder does not contain published content
          or approved content recursively (self.is_published()).
        """
        user = getSecurityManager().getUser()
        if user.has_permission(SilvaPermissions.ApproveSilvaContent, self):
            return True

        return not self.is_published() and not self.is_approved()

    # Silva addables

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_silva_addables_allowed_in_container')
    def set_silva_addables_allowed_in_container(self, addables):
        self._addables_allowed_in_container = addables

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_silva_addables_allowed_in_container')
    def get_silva_addables_allowed_in_container(self):
        return self._addables_allowed_in_container

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_silva_addables_acquired')
    def is_silva_addables_acquired(self):
        return self._addables_allowed_in_container is None

    # get_container API

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_container')
    def get_container(self):
        """Get the container an object is in. Can be used with
        acquisition to get the 'nearest' container.
        FIXME: currently the container of a container is itself. Is this the
        right behavior? It leads to subtle bugs..
        """
        return self.aq_inner

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_real_container')
    def get_real_container(self):
        """Get the container, even if we're a container.

        If we're the root object, returns None.

        Can be used with acquisition to get the 'nearest' container.
        """
        container = self.get_container()
        if container is self:
            return container.aq_parent.get_container()
        return container

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'allow_feeds')
    def allow_feeds(self):
        """return the flag that indicates whether rss/atom feeds are allowed
        on this container"""
        return self._allow_feeds

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_transparent')
    def is_transparent(self):
        return 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_published')
    def is_published(self):
        # Folder is published if its default document is published, or,
        # when no default document exists, if any of the objects it contains
        # are published.
        default = self.get_default()
        if default:
            return default.is_published()
        for object in self.get_ordered_publishables():
            if object.is_published():
                return 1
        return 0

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_approved')
    def is_approved(self):
        # Folder is approved if anything inside is approved
        default = self.get_default()
        if default and default.is_approved():
            return 1
        for object in self.get_ordered_publishables():
            if object.is_approved():
                return 1
        return 0

    def is_deletable(self):
        """deletable if all containing objects are deletable

            NOTE: this will be horribly slow for large trees
        """
        default = self.get_default()
        if default and not default.is_deletable():
            return 0
        for object in self.get_ordered_publishables():
            if not object.is_deletable():
                return 0
        return 1


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_default')
    def get_default(self):
        """Get the default content object of the folder.
        """
        if not hasattr(self.aq_base, 'index'):
            return None
        else:
            return getattr(self, 'index')

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_default_viewable')
    def get_default_viewable(self):
        """Get the viewable version of the default content object
        of this container.
        """
        # Returns None if there's no default, or the default has no
        # viewable version.
        default = self.get_default()
        if default is None:
            return None
        return default.get_viewable()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_ordered_publishables')
    def get_ordered_publishables(self):
        def get_publishable(key):
            try:
                content = self._getOb(key)
            except AttributeError:
                return None
            if isinstance(content, BrokenClass):
                return None
            return content
        return filter(lambda o: o is not None,
                      map(get_publishable, self._ordered_ids))

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_non_publishables')
    def get_non_publishables(self):
        result = self.objectValues(meta_types_for_interface(INonPublishable))
        result.sort(lambda x,y: cmp(x.getId(), y.getId()))
        return result

InitializeClass(Folder)


@silvaconf.subscribe(IFolder, OFS.interfaces.IObjectWillBeMovedEvent)
def folder_moved_update_quota(obj, event):
    """Event called on folder, when they are moved, we want to update
    the quota on parents folders.
    """
    if obj != event.object:
        return
    if IRoot.providedBy(obj):
        return                  # Root is being destroyed, we don't
                                # care about quota anymore.
    if event.newParent is event.oldParent: # For rename event, we
                                           # don't need to do
                                           # something.
        return

    context = event.newParent or event.oldParent
    if not context.service_extensions.get_quota_subsystem_status():
        return

    size = obj.used_space
    if not size:
        return
    if event.oldParent:
        event.oldParent.update_quota(-size)
    if event.newParent:
        event.newParent.update_quota(size)



# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt


import logging

from five import grok
from zope.container.contained import notifyContainerModified
from zope.event import notify
from zope.lifecycleevent import ObjectRemovedEvent
from zope.traversing.browser import absoluteURL

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.Folder import Folder as BaseFolder
from OFS.event import ObjectWillBeRemovedEvent
from OFS.subscribers import compatibilityCall

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva import helpers
from Products.Silva.ExtensionRegistry import meta_types_for_interface
from Products.Silva.Publishable import Publishable
from Products.Silva.QuotaObject import QuotaContainer

from silva.core.interfaces import (
    INonPublishable, IPublishable, IOrderManager,
    IVersionedContent, IFolder, IContent)
from silva.core import conf as silvaconf
from silva.core.interfaces import ContentError
from silva.translations import translate as _

logger = logging.getLogger('silva.core')
_marker = object()


class Folder(Publishable, QuotaContainer, BaseFolder):
    __doc__ = _("""The presentation of the information within a
       publication is structured with folders. They determine the visual
       hierarchy that a Visitor sees. Folders on the top level
       define sections of a publication, subfolders define chapters, etc.
       Note that unlike publications, folders are transparent, meaning you
       can see through them in the sidebar tree navigation and the Publish
       screen.
    """)
    meta_type = "Silva Folder"

    grok.implements(IFolder)
    silvaconf.icon('icons/folder.gif')
    silvaconf.priority(-5)

    security = ClassSecurityInfo()

    @property
    def manage_options(self):
        # A hackish way to get a Silva tab in between the standard ZMI tabs
        manage_options = (BaseFolder.manage_options[0], )
        return manage_options + \
            ({'label':'Silva /edit...', 'action':'edit'}, ) + \
            BaseFolder.manage_options[1:]

    _allow_feeds = False

    def __init__(self, id):
        super(Folder, self).__init__(id)
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
            self._objects = tuple([i for i in self._objects
                                   if i['id'] != identifier])
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

    # Override ObjectManager _getOb to publish any approved for future
    # content. This is the only entry point available when the content
    # is fetched from the database.
    def _getOb(self, id, default=_marker):
        content = super(Folder, self)._getOb(id, default)
        if content is _marker:
            raise AttributeError(id)
        if IVersionedContent.providedBy(content):
            if not hasattr(content, '_v_publication_status_updated'):
                try:
                    content._update_publication_status()
                    content._v_publication_status_updated = True
                except:
                    logger.exception(
                        u"error while updating publication status for: %s",
                        '/'.join(self.getPhysicalPath() + (id,)))
        return content

    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'set_allow_feeds')
    def set_allow_feeds(self, allow):
        """change the flag that indicates whether rss/atom feeds are allowed
        on this container"""
        self._allow_feeds = allow

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'to_publication')
    def to_publication(self):
        """Turn this folder into a publication.
        """
        from Products.Silva.Publication import Publication
        helpers.convert_content(self, Publication)

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'to_folder')
    def to_folder(self):
        """Turn this folder into a folder.
        """
        raise ContentError(
            _(u"You cannot convert a folder into a folder."), self)

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
        for content in self.get_ordered_publishables():
            if content.is_published():
                return True
        return False

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'is_approved')
    def is_approved(self):
        # Folder is approved if anything inside is approved
        default = self.get_default()
        if default and default.is_approved():
            return True
        for content in self.get_ordered_publishables():
            if content.is_approved():
                return True
        return False

    def is_deletable(self):
        """deletable if all containing objects are deletable

            NOTE: this will be horribly slow for large trees
        """
        default = self.get_default()
        if default is not None:
            default.is_deletable()
        for content in self.get_ordered_publishables():
            content.is_deletable()


    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
        return [self.id, self.get_title()]

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_default')
    def get_default(self):
        """Get the default content object of the folder.
        """
        content = self._getOb('index', None)
        if IContent.providedBy(content):
            return content
        return None

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_ordered_publishables')
    def get_ordered_publishables(self, interface=IPublishable):
        assert interface.isOrExtends(IPublishable), u"Invalid interface"
        result = filter(
            lambda content: not content.is_default(),
            self.objectValues(meta_types_for_interface(interface)))
        result.sort(key=IOrderManager(self).get_position)
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_non_publishables')
    def get_non_publishables(self, interface=INonPublishable):
        assert interface.isOrExtends(INonPublishable), u"Invalid interface"
        result = self.objectValues(meta_types_for_interface(interface))
        result.sort(key=lambda o: o.getId())
        return result

InitializeClass(Folder)




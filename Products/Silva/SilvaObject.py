# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from zope.component import getUtility
from zope.container.interfaces import IContainerModifiedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.interfaces import IObjectClonedEvent
from OFS.interfaces import IObjectWillBeAddedEvent
from OFS.interfaces import IObjectWillBeMovedEvent

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Security import Security, ChangesTask

# Silva adapters
from silva.core.interfaces import ISilvaObject, IVersionedContent
from silva.core.services.interfaces import ICataloging
from silva.core.services.interfaces import IMetadataService


class TitledObject(object):
    """Object with a Title stored in the metadata.
    """
    security = ClassSecurityInfo()

    def __init__(self, id):
        super(TitledObject, self)
        self.id = id

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_title')
    def set_title(self, title):
        """Set the title of the silva object.
        """
        if title is not None:
            binding = getUtility(IMetadataService).getMetadata(self)
            binding.setValues('silva-content', {'maintitle': title}, reindex=1)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title')
    def get_title(self):
        """Get the title of the silva object.
        """
        return getUtility(IMetadataService).getMetadataValue(
            self, 'silva-content', 'maintitle')

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get the title of the silva object.
        """
        service = getUtility(IMetadataService)
        title = service.getMetadataValue(
            self, 'silva-content', 'shorttitle')
        if not title.strip():
            title = service.getMetadataValue(
                self, 'silva-content', 'maintitle')
        if not title.strip():
            title = self.get_silva_object().id
        return title

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title_or_id')
    def get_title_or_id(self):
        """Get title or id if not available.
        """
        title = self.get_title()
        if not title.strip():
            title = self.get_silva_object().id
        return title

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title_editable')
    def get_title_editable(self):
        """Get the title of the editable version if possible.
        """
        return self.get_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title_editable')
    def get_short_title_editable(self):
        """Get the short title of the editable version if possible.
        """
        return self.get_short_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title_or_id_editable')
    def get_title_or_id_editable(self):
        """Get the title of the editable version if possible, or id if
        not available.
        """
        title = self.get_title_editable()
        if not title.strip():
            return self.get_silva_object().id
        return title

InitializeClass(TitledObject)


class SilvaObject(TitledObject, Security):
    """Inherited by all Silva objects.
    """
    security = ClassSecurityInfo()

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_silva_object')
    def get_silva_object(self):
        """Get the object. Can be used with acquisition to get the Silva
        Document for a Version object.
        """
        return self.aq_inner

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_creation_datetime')
    def get_creation_datetime(self):
        """Return creation datetime."""
        version = self.get_previewable()
        return getUtility(IMetadataService).getMetadataValue(
            version, 'silva-extra', 'creationtime')

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_modification_datetime')
    def get_modification_datetime(self):
        """Return modification datetime."""
        version = self.get_previewable()
        return getUtility(IMetadataService).getMetadataValue(
            version, 'silva-extra', 'modificationtime')

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_editable')
    def get_editable(self):
        """Get the editable version (may be object itself if no versioning).
        """
        return self.aq_inner

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
        'is_deletable')
    def is_deletable(self):
        """always deletable"""
        pass


InitializeClass(SilvaObject)


class ViewableObject(object):
    """Content that can be displayed to the public.
    """
    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'get_previewable')
    def get_previewable(self):
        """Get the previewable version (may be the object itself if no
        versioning).
        """
        return self.aq_inner

    security.declareProtected(SilvaPermissions.View, 'get_viewable')
    def get_viewable(self):
        """Get the publically viewable version (may be the object itself if
        no versioning).
        """
        return self.aq_inner

InitializeClass(ViewableObject)


@grok.subscribe(ISilvaObject, IObjectCreatedEvent)
@grok.subscribe(ISilvaObject, IObjectClonedEvent)
def content_created(content, event):
    if (content != event.object or
        IObjectCopiedEvent.providedBy(event) or
        IVersionedContent.providedBy(content)):
        return

    ICataloging(content).index()
    ChangesTask.get().modified(content, created=True)


@grok.subscribe(ISilvaObject, IObjectModifiedEvent)
def index_and_update_author_modified_content(content, event):
    """A content have been created of modifed. Update its author
    information.
    """
    # In the same way, we discard event on versioned content if they
    # are about adding or removing a version.
    if (IVersionedContent.providedBy(content) and
        IContainerModifiedEvent.providedBy(event)):
        return
    if getattr(content, '__initialization__', False):
        return
    ChangesTask.get().modified(content)
    ICataloging(content).reindex()


@grok.subscribe(ISilvaObject, IObjectMovedEvent)
def index_moved_content(content, event):
    """We index all added content (due to a move).
    """
    if getattr(content, '__initialization__', False):
        return

    if (not IObjectAddedEvent.providedBy(event) and
        not IObjectRemovedEvent.providedBy(event)):
        ICataloging(content).index()


@grok.subscribe(ISilvaObject, IObjectWillBeMovedEvent)
def unindex_removed_content(content, event):
    """We unindex all content that is going to be moved, and/or
    deleted.
    """
    if not IObjectWillBeAddedEvent.providedBy(event):
        ICataloging(content).unindex()

# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from OFS.interfaces import IObjectClonedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.interfaces import IObjectWillBeRemovedEvent

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.SilvaObject import TitledObject
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.Silva.Security import Security, ChangesTask

from silva.core.interfaces import IVersion, VersioningError
from silva.core.interfaces import IVersionManager
from silva.core.interfaces.events import IApprovalEvent
from silva.core.interfaces.events import IContentClosedEvent
from silva.core.interfaces.events import IContentPublishedEvent
from silva.core.interfaces.events import IPublishingEvent
from silva.core.services.interfaces import ICataloging
from silva.translations import translate as _


class Version(Security, TitledObject, SimpleItem):
    """A Version of a versioned content.
    """
    grok.implements(IVersion)
    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_version')
    def get_version(self):
        """Returns itself. Used by acquisition to get the
           neared version.
        """
        return self.aq_inner


InitializeClass(Version)


class VersionManager(grok.Adapter):
    """Adapter to manage Silva versions
    """
    grok.implements(IVersionManager)
    grok.provides(IVersionManager)
    grok.context(IVersion)

    def __init__(self, version):
        self.version = version
        self.content = version.get_silva_object()

    def make_editable(self):
        """Make the version editable.
        """
        current_version = self.content.get_unapproved_version()
        if current_version is not None:
            # move the current editable version to _previous_versions
            if self.content.is_approval_requested():
                raise VersioningError(
                    _('A version is already waiting approval.'),
                    self)

            version_tuple = self.content._unapproved_version
            if self.content._previous_versions is None:
                self.content._previous_versions = []
            self.content._previous_versions.append(version_tuple)
            self.content._unapproved_version = (None, None, None)

        self.content.create_copy(version_id=self.version.id)
        return True

    def delete(self):
        """Delete the version
        """
        versionid = self.version.id

        if self.content.get_approved_version() == versionid:
            raise VersioningError(
                _(u"Version is approved."),
                self.content, self.version)

        if self.content.get_public_version() == versionid:
            raise VersioningError(
                _(u"Version is published."),
                self.content, self.version)

        if self.content.get_unapproved_version() == versionid:
            self.content._unapproved_version = (None, None, None)
        else:
            for version in self.content._previous_versions:
                if version[0] == versionid:
                    self.content._previous_versions.remove(version)
                    break
        self.content.manage_delObjects([versionid])
        return True

    def get_modification_datetime(self):
        return getUtility(IMetadataService).getMetadataValue(
            self.version, 'silva-extra', 'modificationtime')

    def __get_version_tuple(self):
        versionid = self.version.id
        if self.content.get_unapproved_version() == versionid:
            return self.content._unapproved_version
        elif self.content.get_approved_version() == versionid:
            return self.content._approved_version
        elif self.content.get_public_version() == versionid:
            return self.content._public_version
        elif self.content._previous_versions:
            for info in self.content._previous_versions:
                if info[0] == versionid:
                    return info
        return (None, None, None)

    def get_publication_datetime(self):
        return self.__get_version_tuple()[1]

    def get_expiration_datetime(self):
        return self.__get_version_tuple()[2]

    def get_last_author(self):
        return self.version.get_last_author_info()

    def get_status(self):
        """Returns the status of a version as a string

            return value can be one of the following strings:

                unapproved
                pending
                approved
                published
                last_closed
                closed
        """
        versionid = self.version.id
        if self.content.get_unapproved_version() == versionid:
            if self.content.is_approval_requested():
                return 'pending'
            return 'unapproved'
        elif self.content.get_approved_version() == versionid:
            return 'approved'
        elif self.content.get_public_version() == versionid:
            return 'published'
        else:
            if self.content._previous_versions:
                if self.content._previous_versions[-1][0] == versionid:
                    return 'last_closed'
                else:
                    for (vid, vpt, vet) in self.content._previous_versions:
                        if vid == versionid:
                            return 'closed'
        raise VersioningError(
            _('No such version ${version}',
              mapping={'version': versionid}),
            self.content)


_i18n_markers = (_('unapproved'), _('approved'), _('last_closed'),
                 _('closed'), _('draft'), _('pending'), _('public'),)


@grok.subscribe(IVersion, IObjectCreatedEvent)
@grok.subscribe(IVersion, IObjectClonedEvent)
def version_created(version, event):
    if IObjectCopiedEvent.providedBy(event):
        return

    created = version == event.object
    ChangesTask.get().modified(version, created)
    if created:
        ICataloging(version).index()
        ICataloging(version.get_silva_object()).index(with_versions=False)


@grok.subscribe(IVersion, IApprovalEvent)
@grok.subscribe(IVersion, IContentPublishedEvent)
def version_published(version, event):
    ChangesTask.get().modified(version)
    ICataloging(version).reindex()
    ICataloging(version.get_silva_object()).reindex(with_versions=False)


@grok.subscribe(IVersion, IContentClosedEvent)
def version_closed(version, event):
    ChangesTask.get().modified(version)
    ICataloging(version).unindex()
    ICataloging(version.get_silva_object()).reindex(with_versions=False)


@grok.subscribe(IVersion, IObjectModifiedEvent)
def version_modified(version, event):
    if not IPublishingEvent.providedBy(event):
        # This version have been modified
        ChangesTask.get().modified(version)
        ICataloging(version).reindex()
        ICataloging(version.get_silva_object()).reindex(with_versions=False)


@grok.subscribe(IVersion, IObjectWillBeRemovedEvent)
def version_removed(version, event):
    if version == event.object:
        # Only interested about version removed by hand.
        ICataloging(version).unindex()



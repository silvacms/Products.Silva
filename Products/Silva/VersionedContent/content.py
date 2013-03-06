# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo
from AccessControl.security import checkPermission
from App.class_init import InitializeClass
from OFS.Folder import Folder as BaseFolder

# Silva
from Products.Silva import SilvaPermissions as permissions
from Products.Silva.Content import Content
from Products.Silva.Publishable import NonPublishable
from Products.Silva.SilvaObject import SilvaObject, ViewableObject
from Products.Silva.Versioning import Versioning
from Products.Silva.Membership import noneMember

from silva.translations import translate as _
from silva.core.interfaces import IVersionedContent, ContentError
from silva.core.interfaces import IVersionedObject
from silva.core.interfaces import IVersionedNonPublishable


class VersionedObject(Versioning, SilvaObject, ViewableObject):
    security = ClassSecurityInfo()
    grok.implements(IVersionedObject)
    grok.baseclass()

    # there is always at least a single version to start with,
    # created by the object's factory function
    _version_count = 1

    # Set ZMI tabs
    manage_options = (
        (BaseFolder.manage_options[0], ) +
        ({'label': 'Silva /edit...', 'action':'edit'},)+
        BaseFolder.manage_options[1:])

    # MANIPULATORS

    security.declareProtected(
        permissions.ChangeSilvaContent, 'set_title')
    def set_title(self, title):
        """Set title of version under edit.
        """
        editable = self.get_editable()
        if editable is None:
            return
        editable.set_title(title)

    # ACCESSORS
    security.declareProtected(
        permissions.AccessContentsInformation, 'get_title')
    def get_title(self):
        """Get title for public use, from published version.
        """
        version = self.get_viewable()
        if version is None:
            return ""
        return version.get_title()

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_title_editable')
    def get_title_editable(self):
        """Get title for editable or previewable use
        """
        # Ask for 'previewable', which will return either the 'next version'
        # (which may be under edit, or is approved), or the public version,
        # or, as a last resort, the closed version.
        # This to be able to show at least some title in the Silva edit
        # screens.
        version = self.get_previewable()
        if version is None:
            return ""
        return version.get_title_editable()

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short_title for public use, from published version.
        """
        version = self.get_viewable()
        if version is None:
            return self.id
        return version.get_short_title()

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_short_title_editable')
    def get_short_title_editable(self):
        """Get short_title for editable or previewable use
        """
        version = self.get_previewable()
        if version is None:
            return self.id
        return version.get_short_title_editable()

    security.declareProtected(permissions.ChangeSilvaContent,
                              'get_editable')
    def get_editable(self):
        """Get the editable version (may be object itself if no versioning).
        """
        # the editable version is the unapproved version
        version_id = self.get_unapproved_version()
        if version_id is None:
            return None # there is no editable version
        return self._getOb(version_id, None)

    security.declareProtected(permissions.ReadSilvaContent,
                              'get_previewable')
    def get_previewable(self):
        """Get the previewable version (may be the object itself if no
        versioning).
        """
        version_id = self.get_next_version()
        if version_id is None:
            version_id = self.get_public_version()
            if version_id is None:
                version_id = self.get_last_closed_version()
                if version_id is None:
                    return None
        return self._getOb(version_id, None)

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_viewable')
    def get_viewable(self):
        """Get the publically viewable version (may be the object itself if
        no versioning).
        """
        version_id = self.get_public_version()
        if version_id is None:
            return None # There is no public document
        return self._getOb(version_id, None)

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_last_author_info')
    def get_last_author_info(self):
        previewable = self.get_previewable()
        if previewable is not None:
            return previewable.get_last_author_info()
        return noneMember.__of__(self)

    security.declareProtected(
        permissions.AccessContentsInformation, 'is_deletable')
    def is_deletable(self):
        """is object deletable?

            a publishable object is only deletable if
                it's not published
                it's not approved

        """
        if not checkPermission('silva.ApproveSilvaContent', self):
            if self.is_published():
                raise ContentError(
                    _(u"Content is published."),
                    self)
            if self.is_approved():
                raise ContentError(
                    _(u"Content is approved."),
                    self)

InitializeClass(VersionedObject)


class VersionedContent(VersionedObject, Content, BaseFolder):
    grok.implements(IVersionedContent)
    grok.baseclass()


class VersionedNonPublishable(VersionedObject, NonPublishable, BaseFolder):
    grok.implements(IVersionedNonPublishable)
    grok.baseclass()

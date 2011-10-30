# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo, getSecurityManager
from App.class_init import InitializeClass
from OFS.Folder import Folder as BaseFolder

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Versioning import Versioning
from Products.Silva.Content import Content

from silva.translations import translate as _
from silva.core.interfaces import IVersionedContent, ContentError


class VersionedContent(Versioning, Content, BaseFolder):
    security = ClassSecurityInfo()

    grok.implements(IVersionedContent)
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

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        """Set title of version under edit.
        """
        editable = self.get_editable()
        if editable is None:
            return
        editable.set_title(title)

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                             'get_title')
    def get_title(self):
        """Get title for public use, from published version.
        """
        viewable = self.get_viewable()
        if viewable is None:
            return ""
        return viewable.get_title()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title_editable')
    def get_title_editable(self):
        """Get title for editable or previewable use
        """
        # Ask for 'previewable', which will return either the 'next version'
        # (which may be under edit, or is approved), or the public version,
        # or, as a last resort, the closed version.
        # This to be able to show at least some title in the Silva edit
        # screens.
        previewable = self.get_previewable()
        if previewable is None:
            return ""
        return previewable.get_title_editable()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title_or_id_editable')
    def get_title_or_id_editable(self):
        """Get title or id editable or previewable use.
        """
        title = self.get_title_editable()
        if title.strip() == '':
            return self.id
        return title

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short_title for public use, from published version.
        """
        viewable = self.get_viewable()
        if viewable is None:
            return self.id
        return viewable.get_short_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title_editable')
    def get_short_title_editable(self):
        """Get short_title for editable or previewable use
        """
        previewable = self.get_previewable()
        if previewable is None:
            return self.id
        return previewable.get_short_title()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_editable')
    def get_editable(self):
        """Get the editable version (may be object itself if no versioning).
        """
        # the editable version is the unapproved version
        version_id = self.get_unapproved_version()
        if version_id is None:
            return None # there is no editable version
        return getattr(self, version_id)

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
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
        return getattr(self, version_id)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_viewable')
    def get_viewable(self):
        """Get the publically viewable version (may be the object itself if
        no versioning).
        """
        version_id = self.get_public_version()
        if version_id is None:
            return None # There is no public document
        return getattr(self, version_id)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
        'is_deletable')
    def is_deletable(self):
        """is object deletable?

            a publishable object is only deletable if
                it's not published
                it's not approved

        """
        check_permission = getSecurityManager().checkPermission
        if not check_permission('Approve Silva content', self):
            if self.is_published():
                raise ContentError(
                    _(u"Content is published."),
                    self)
            if self.is_approved():
                raise ContentError(
                    _(u"Content is approved."),
                    self)

InitializeClass(VersionedContent)

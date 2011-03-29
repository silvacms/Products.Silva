# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator

# Zope 3
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base
from App.class_init import InitializeClass
from OFS.Folder import Folder as BaseFolder
from zExceptions import NotFound
from DateTime import DateTime
from datetime import datetime

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Versioning import Versioning
from Products.Silva.Content import Content

from silva.core.interfaces import IVersion
from silva.core.interfaces import IVersionedContent
from silva.core.interfaces import IPublicationWorkflow, PublicationWorkflowError
from silva.core.services.catalog import Cataloging
from silva.core.services.interfaces import ICataloging, ICatalogingAttributes
from silva.translations import translate as _


class VersionedContent(Content, Versioning, BaseFolder):
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
    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """Check to see if the title can be set
        """
        return bool(self.get_editable())

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                             'get_title')
    def get_title(self):
        """Get title for public use, from published version.
        """
        viewable = self.get_viewable()
        if viewable is None:
            return self.id
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
            return "[No title available]"
        return previewable.get_title()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title_or_id_editable')
    def get_title_or_id_editable(self):
        """Get title or id editable or previewable use.
        """
        title = self.get_title_editable()
        if title.strip() == '':
            return self.id
        else:
            return title

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short_title for public use, from published version.
        """
        # Analogous to get_title
        viewable = self.get_viewable()
        if viewable is None:
            return self.id
        return viewable.get_short_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title_editable')
    def get_short_title_editable(self):
        """Get short_title for editable or previewable use
        """
        # Analogous to get_title_editable
        previewable = self.get_previewable()
        if previewable is None:
            return "[No (short) title available]"
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
                              'get_last_closed')
    def get_last_closed(self):
        """Get the last closed version (may be the object itself if
        no versioning).
        """
        version_id = self.get_last_closed_version()
        if version_id is None:
            return None # There is no public document
        return getattr(self, version_id)

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'view_version')
    def view_version(self, version=None):
        version_name = self.REQUEST.other.get('SILVA_PREVIEW_NAME', '')
        if version_name:
            version = getattr(self, version_name, None)
            if version is None:
                raise NotFound(version_name)
        return super(VersionedContent, self).view_version(version)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
        'is_deletable')
    def is_deletable(self):
        """is object deletable?

            a publishable object is only deletable if
                it's not published
                it's not approved

        """
        if getSecurityManager().checkPermission('Approve Silva content', self):
            return True
        return not self.is_published() and not self.is_approved()

    def _index_version(self, version_id):
        version = getattr(self, version_id, None)
        if version is not None:
            # XXX Update this
            ICataloging(version).index()

    def _reindex_version(self, version_id):
        version = getattr(self, version_id, None)
        if version is not None:
            # XXX Update this
            ICataloging(version).reindex()

    def _unindex_version(self, version_id):
        version = getattr(self, version_id, None)
        if version is not None:
            # XXX Update this
            ICataloging(version).unindex()


InitializeClass(VersionedContent)


class VersionedContentCataloging(Cataloging):
    """Cataloging support for versioned content.
    """
    grok.context(IVersionedContent)

    def get_indexable_versions(self):
        version_ids = [
            self.context.get_next_version(),
            self.context.get_public_version()]
        for version_id in version_ids:
            if version_id is None:
                continue
            if hasattr(aq_base(self.context), version_id):
                yield getattr(self.context, version_id)

    def index(self, indexes=None):
        if self._catalog is None:
            return
        super(VersionedContentCataloging, self).index(indexes=indexes)
        for version in self.get_indexable_versions():
            attributes = ICatalogingAttributes(version)
            path = '/'.join((self._path, version.getId(),))
            self._catalog.catalog_object(attributes, path)

    def unindex(self):
        if self._catalog is None:
            return
        super(VersionedContentCataloging, self).unindex()
        for version in self.get_indexable_versions():
            path = '/'.join((self._path, version.getId(),))
            self._catalog.uncatalog_object(path)


class VersionedContentPublicationWorkflow(grok.Adapter):
    grok.context(IVersionedContent)
    grok.implements(IPublicationWorkflow)
    grok.provides(IPublicationWorkflow)

    def new_version(self):
        if self.context.get_unapproved_version() is not None:
            raise PublicationWorkflowError(
                _("This content already has a new version."))
        self.context.create_copy()
        return True

    def request_approval(self, message):
        # XXX add checkout publication datetime
        # set_unapproved_version_publication_datetime(DateTime())
        if self.context.get_unapproved_version() is None:
            raise PublicationWorkflowError(
                _('There is no unapproved version.'))
        if self.context.is_version_approval_requested():
            raise PublicationWorkflowError(
                _('Approval has already been requested.'))
        self.context.request_version_approval(message)
        return True

    def _check_withdraw_or_reject(self):
        if self.context.get_unapproved_version() is None:
            if self.context.get_public_version() is not None:
                raise PublicationWorkflowError(
                    _("This content is already public."))
            else:
                raise PublicationWorkflowError(
                    _("This content is already approved."))
        if not self.context.is_version_approval_requested():
            raise PublicationWorkflowError(
                _("No request for approval is pending for this content."))

    def withdraw_request(self, message):
        self._check_withdraw_or_reject()
        self.context.withdraw_version_approval(message)
        return True

    def reject_request(self, message):
        self._check_withdraw_or_reject()
        self.context.reject_version_approval(message)
        return True

    def revoke_approval(self):
        if self.get_approved_version():
            self.context.unapprove_version()
            return True
        raise PublicationWorkflowError(
            _(u"This content is not approved."))

    def approve(self, time=None):
        if time is None:
            time = DateTime()
        elif isinstance(time, datetime):
            time = DateTime(time)
        if self.context.get_unapproved_version() is None:
            raise PublicationWorkflowError(
                _("There is no unapproved version to approve."))
        self.context.set_unapproved_version_publication_datetime(time)
        self.context.approve_version()
        return True

    def publish(self, time=None):
        # Do the same job than approve, but works on closed content as
        # well.
        if not self.context.get_unapproved_version():
            if self.context.is_version_published():
                raise PublicationWorkflowError(
                    _("There is no unapproved version to approve."))
            self.context.create_copy()
        self.approve(time)
        return True

    def close(self):
        if self.context.get_public_version() is None:
            raise PublicationWorkflowError(
                _("There is no public version to close"))
        self.context.close_version()
        return True

    def get_versions(self, sort_attribute='id'):
        versions = filter(IVersion.providedBy, self.context.objectValues())
        if sort_attribute == 'id':
            versions.sort(key=lambda a: int(a.id))
        elif sort_attribute:
            versions.sort(key=operator.attrgetter(sort_attribute))
        return versions


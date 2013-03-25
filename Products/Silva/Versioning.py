# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime

from five import grok
from zope.event import notify

# Zope 2
from AccessControl import ClassSecurityInfo, getSecurityManager
from App.class_init import InitializeClass
from DateTime import DateTime

# Silva
from Products.Silva import SilvaPermissions

from silva.core.interfaces import events
from silva.core.interfaces import IVersioning, IVersion, VersioningError
from silva.core.interfaces import IRequestForApprovalStatus
from silva.translations import translate as _

empty_version = (None, None, None)


class RequestForApprovalMessage(object):
    """Message about the request for approval status.
    """

    def __init__(self, status, message):
        self.user_id = getSecurityManager().getUser().getId()
        self.date = datetime.now()
        self.message = message
        self.status = status


class RequestForApprovalStatus(grok.Annotation):
    """Simple helper class storing information about the current
    request for approval.
    """
    grok.context(IVersion)
    grok.implements(IRequestForApprovalStatus)

    def __init__(self):
        self.pending = False
        self.messages = []

    def comment(self, status, message=None):
        self.messages.append(RequestForApprovalMessage(status, message))
        self.pending = (status == 'request')

    def validate(self):
        if self.pending:
            self.comment('approve')
            self.pending = False

    def reset(self):
        self.pending = False
        self.messages = []


class Versioning(object):
    """Mixin baseclass to make object contents versioned.
    """
    grok.implements(IVersioning)
    security = ClassSecurityInfo()

    # TODO: Silva 3.1: The datetime expiration and publication are
    # currently stored inside the VersionedContent. Moving it to the
    # Version would simplify a lot the management of the versions.
    _unapproved_version = empty_version
    _approved_version = empty_version
    _public_version = empty_version
    _previous_versions = None
    _first_publication_date = None

    # MANIPULATORS
    security.declarePrivate('create_version')
    def create_version(self, version_id,
                       publication_datetime,
                       expiration_datetime):
        """Add unapproved version
        """

        assert self._approved_version == empty_version, \
            u'There is an approved version'

        assert self._unapproved_version == empty_version, \
            u'There is an unapproved version'

        # if a version with this name already exists, complain
        if self._public_version is not None:
            assert version_id != self._public_version[0], \
                u'There is already a public version with the same id'

        previous_versions = self._previous_versions or []
        for previous_version in previous_versions:
            assert version_id != previous_version[0], \
                u'There is already a previous version with the same id'

        self._unapproved_version = (version_id,
                                    publication_datetime,
                                    expiration_datetime)

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'approve_version')
    def approve_version(self):
        """Aprove the current unapproved version.
        """
        # self._update_publication_status()
        if self._unapproved_version == empty_version:
            raise VersioningError(
                _('There is no unapproved version to approve.'),
                self)

        if self._approved_version != empty_version:
            raise VersioningError(
                _('There already is an approved version.'),
                self)

        if self._unapproved_version[1] is None:
            raise VersioningError(
                _('Cannot approve version without publication datetime.'),
                self)

        self._approved_version = self._unapproved_version
        self._unapproved_version = empty_version

        version = self._getOb(self._approved_version[0])
        status = IRequestForApprovalStatus(version)
        status.validate()

        notify(events.ContentApprovedEvent(version, status))

        # We may be published now
        self._update_publication_status()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'unapprove_version')
    def unapprove_version(self):
        """Unapprove an approved but not yet public version.
        """
        # self._update_publication_status()
        if self._approved_version == empty_version:
            raise VersioningError(
                  _("This content is not approved."),
                  self)

        if self._unapproved_version != empty_version:
            raise VersioningError(
                _(('Should never happen: unapproved version ${unapproved} found while '
                   'approved version ${approved} exists at the same time.'),
                  mapping={'unapproved': self._unapproved_version[0],
                           'approved': self._approved_version[0]}),
                self)

        self._unapproved_version = self._approved_version
        self._approved_version = empty_version

        version = self._getOb(self._unapproved_version[0])
        notify(events.ContentUnApprovedEvent(version))


    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'close_version')
    def close_version(self):
        """Close public version.
        """
        if self._public_version == empty_version:
            raise VersioningError(
                _(u"There is no public version to close."),
                self)

        previous_versions = self._previous_versions or []
        previous_versions.append(self._public_version)
        self._public_version = empty_version
        self._previous_versions = previous_versions

        version = self._getOb(self._previous_versions[-1][0])
        notify(events.ContentClosedEvent(version))

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'create_copy')
    def create_copy(self, version_id=None):
        """Create new version of public version.
        """
        if self.get_approved_version() is not None:
            raise VersioningError(
                _('An approved version is already available.'),
                self)
        if self.get_unapproved_version() is not None:
            raise VersioningError(
                _('An new version is already available.'),
                self)

        expiration_time = None
        if version_id is None:
            # get id of public version to copy
            version_id, ignored_time, expiration_time = self._public_version
            # if there is no public version, get id of last closed version
            # (which should always be there)
            if version_id is None:
                if self._previous_versions:
                    version_id, ignored_time, expiration_time = \
                        self._previous_versions[-1]
                if version_id is None:
                    raise VersioningError(
                        _(u"There is no version to create a version form."),
                        self)
        if expiration_time is not None and not expiration_time.isFuture():
            # Reset expiration time if it is in the past.
            expiration_time = None

        # Copy given version
        new_version_id = self.get_new_version_id()
        self.manage_clone(self._getOb(version_id), new_version_id)

        # The version might have been copied. Clear its data.
        version = self._getOb(new_version_id)
        IRequestForApprovalStatus(version).reset()

        # Register it
        self.create_version(new_version_id, None, expiration_time)

    security.declarePrivate('get_new_version_id')
    def get_new_version_id(self):
        """get_new_version_id is used when a new version will be created,
        to get a new unique id.  This may or may not change internal
        variables"""
        new_version_id = str(self._version_count)
        self._version_count = self._version_count + 1
        return str(new_version_id)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'request_version_approval')
    def request_version_approval(self, message):
        """Request approval for the current unapproved version
        Raises VersioningError, if there is no such version,
        or it is already approved.
        Returns None otherwise
        """
        version_id = self.get_unapproved_version()
        if version_id is None:
            raise VersioningError(
                _("This content doesn't require approval."),
                self)

        version = self._getOb(version_id)
        status = IRequestForApprovalStatus(version)
        if status.pending:
            raise VersioningError(
                _('The version is already requested for approval.'),
                self)

        status.comment('request', message)
        notify(events.ContentRequestApprovalEvent(version, status))

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'withdraw_version_approval')
    def withdraw_version_approval(self, message):
        """Withdraw a previous request for approval
        Implementation should raise VersioningError, if the
        currently unapproved version has no request for approval yet,
        or if there is no unapproved version.
        """
        version_id = self.get_unapproved_version()
        if version_id is None:
            raise VersioningError(
                _("This content doesn't require approval."),
                self)

        version = self._getOb(version_id)
        status = IRequestForApprovalStatus(version)
        if not status.pending:
            raise VersioningError(
                _("No request for approval is pending for this content."),
                self)

        status.comment('withdraw', message)
        notify(events.ContentApprovalRequestWithdrawnEvent(version, status))

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'reject_version_approval')
    def reject_version_approval(self, message):
        """Reject a previous request for approval
        Implementation should raise VersioningError, if the
        currently unapproved version has no request for approval yet,
        or if there is no unapproved version.
        """
        version_id = self.get_unapproved_version()
        if version_id is None:
            raise VersioningError(
                _("This content doesn't require approval."),
                self)

        version = self._getOb(version_id)
        status = IRequestForApprovalStatus(version)
        if not status.pending:
            raise VersioningError(
                _("No request for approval is pending for this content."),
                self)

        status.comment('reject', message)
        notify(events.ContentApprovalRequestRefusedEvent(version, status))

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_unapproved_version_publication_datetime')
    def set_unapproved_version_publication_datetime(self, dt):
        """Set publication datetime for unapproved, or None for no
        publication at all yet.
        """
        if self._unapproved_version == empty_version:
            raise VersioningError(_('No unapproved version.'), self)

        version_id, publication_datetime, expiration_datetime = \
                    self._unapproved_version
        self._unapproved_version = version_id, dt, expiration_datetime

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_unapproved_version_expiration_datetime')
    def set_unapproved_version_expiration_datetime(self, dt):
        """Set expiration datetime, or None for no expiration.
        """
        if self._unapproved_version == empty_version:
            raise VersioningError(_('No unapproved version.'), self)

        version_id, publication_datetime, expiration_datetime = \
                    self._unapproved_version
        self._unapproved_version = version_id, publication_datetime, dt

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_approved_version_publication_datetime')
    def set_approved_version_publication_datetime(self, dt):
        """Set publication datetime for approved.
        """
        if self._approved_version == empty_version:
            raise VersioningError(_('No approved version.'), self)

        if dt is None:
            raise VersioningError(_('Must specify publication datetime.'), self)

        version_id, publication_datetime, expiration_datetime = \
                    self._approved_version
        self._approved_version = version_id, dt, expiration_datetime
        # may become published, update publication status
        self._update_publication_status()

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_approved_version_expiration_datetime')
    def set_approved_version_expiration_datetime(self, dt):
        """Set expiration datetime, or None for no expiration.
        """
        if self._approved_version == empty_version:
            raise VersioningError(_('No approved version.'), self)

        version_id, publication_datetime, expiration_datetime = \
                    self._approved_version
        self._approved_version = version_id, publication_datetime, dt
        # may become closed, update publication status
        self._update_publication_status()

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'set_public_version_expiration_datetime')
    def set_public_version_expiration_datetime(self, dt):
        """Set expiration datetime, or None for no expiration.
        """
        if self._public_version == empty_version:
            raise VersioningError(_('No public version.'), self)

        version_id, publication_datetime, expiration_datetime = \
            self._public_version
        self._public_version = version_id, publication_datetime, dt
        # may become expired, update publication status
        self._update_publication_status()

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_next_version_publication_datetime')
    def set_next_version_publication_datetime(self, dt):
        """Set publication datetime of next version.
        """
        if self._approved_version[0]:
            version_id, publication_datetime, expiration_datetime = \
                        self._approved_version
            self._approved_version = version_id, dt, expiration_datetime
            self._update_publication_status()
        elif self._unapproved_version[0]:
            version_id, publication_datetime, expiration_datetime = \
                        self._unapproved_version
            self._unapproved_version = version_id, dt, expiration_datetime
        else:
            raise VersioningError(_('No next version.'), self)

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_next_version_expiration_datetime')
    def set_next_version_expiration_datetime(self, dt):
        """Set expiration datetime of next version.
        """
        if self._approved_version[0]:
            version_id, publication_datetime, expiration_datetime = \
                        self._approved_version
            self._approved_version = version_id, publication_datetime, dt
        elif self._unapproved_version[0]:
            version_id, publication_datetime, expiration_datetime = \
                        self._unapproved_version
            self._unapproved_version = version_id, publication_datetime, dt
        else:
            raise VersioningError(_('No next version.'), self)

    def _update_publication_status(self):
        # Publish what need to be publish, expire what need to be expired
        now = DateTime()
        # get publication datetime of approved version
        publication_datetime = self._approved_version[1]
        # if it is time make approved version public
        if publication_datetime and now >= publication_datetime:
            if self._public_version != empty_version:
                if not self._previous_versions:
                    self._previous_versions = []
                self._previous_versions.append(self._public_version)
                notify(events.ContentClosedEvent(
                        self._getOb(self._public_version[0], None)))
            self._public_version = self._approved_version
            if self._first_publication_date is None:
                self._first_publication_date = publication_datetime
            self._approved_version = empty_version
            notify(events.ContentPublishedEvent(
                    self._getOb(self._public_version[0], None)))
        # get expiration datetime of public version
        expiration_datetime = self._public_version[2]
        # expire public version if expiration datetime reached
        if expiration_datetime and now >= expiration_datetime:
            # make sure to add it to the previous versions
            previous_versions = self._previous_versions or []
            previous_versions.append(self._public_version)
            self._public_version = empty_version
            self._previous_versions = previous_versions
            notify(events.ContentExpiredEvent(
                    self._getOb(self._previous_versions[-1][0], None)))

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'is_approved')
    def is_approved(self):
        """Check whether version is approved.
        """
        return self._approved_version != empty_version

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_published')
    def is_published(self):
        """Check whether version is published.
        """
        return self._public_version != empty_version

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'is_approval_requested')
    def is_approval_requested(self):
        """Check if there exists an unapproved version
        which has a request for approval.
        """
        version_id = self.get_unapproved_version()
        if version_id is None:
            return False

        version = self._getOb(version_id)
        status = IRequestForApprovalStatus(version)
        return status.pending

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_unapproved_version')
    def get_unapproved_version(self):
        """Get the unapproved version.
        """
        return self._unapproved_version[0]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_unapproved_version_data')
    def get_unapproved_version_data(self):
        """Get all the workflow data of the unapproved version.
        """
        return self._unapproved_version

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_unapproved_version_publication_datetime')
    def get_unapproved_version_publication_datetime(self):
        """Get publication datetime."""
        return self._unapproved_version[1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_unapproved_version_expiration_datetime')
    def get_unapproved_version_expiration_datetime(self):
        """Get version datetime."""
        return self._unapproved_version[2]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approved_version')
    def get_approved_version(self):
        """Get the approved version.
        """
        return self._approved_version[0]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approved_version_data')
    def get_approved_version_data(self):
        """Get all the workflow data of the approved version.
        """
        return self._approved_version

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approved_version_publication_datetime')
    def get_approved_version_publication_datetime(self):
        """Get publication datetime."""
        return self._approved_version[1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approved_version_expiration_datetime')
    def get_approved_version_expiration_datetime(self):
        """Get version datetime."""
        return self._approved_version[2]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version')
    def get_next_version(self):
        """Get either approved version if available, or unapproved
        version if not, or None if no next version.
        """
        return self._approved_version[0] or self._unapproved_version[0]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version_publication_datetime')
    def get_next_version_publication_datetime(self):
        """Get publication datetime."""
        return self._approved_version[1] or self._unapproved_version[1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version_expiration_datetime')
    def get_next_version_expiration_datetime(self):
        """Get version datetime."""
        return self._approved_version[2] or self._unapproved_version[2]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_public_version')
    def get_public_version(self):
        """Get the public version.
        """
        return self._public_version[0]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_public_version_data')
    def get_public_version_data(self):
        """Get all workflow data of the public version.
        """
        return self._public_version

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_first_publication_date')
    def get_first_publication_date(self):
        """Get the earliest publication date of any version of this Content.
        Needed for rss/atom feeds.
        """
        if not self._first_publication_date is None:
            return self._first_publication_date
        return self.get_public_version_publication_datetime()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_public_version_publication_datetime')
    def get_public_version_publication_datetime(self):
        """Get publication datetime."""
        return self._public_version[1]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_public_version_expiration_datetime')
    def get_public_version_expiration_datetime(self):
        """Get version datetime."""
        return self._public_version[2]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_previous_versions')
    def get_previous_versions(self):
        """Get list of previous versions, index 0 most recent.
        """
        if self._previous_versions is None:
            return []
        return [version[0] for version in self._previous_versions]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_previous_versions_data')
    def get_previous_versions_data(self):
        """Get list of workflow data of the previous versions, index 0 most
        recent.
        """
        if self._previous_versions is None:
            return []
        return [version for version in self._previous_versions]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_last_closed_version')
    def get_last_closed_version(self):
        """Get the last closed version or None if no such thing.
        """
        versions = self.get_previous_versions()
        if len(versions) < 1:
            return None
        return versions[-1]


InitializeClass(Versioning)


# BBB Pickle for cleanup
class RequestForApprovalInfo(object):
    pass


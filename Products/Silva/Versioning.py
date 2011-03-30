# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.interface import implements
from zope.event import notify

# Zope 2
from AccessControl import ClassSecurityInfo, getSecurityManager
from App.class_init import InitializeClass
from DateTime import DateTime

# Silva
from Products.Silva import SilvaPermissions

from silva.core.interfaces import events
from silva.core.interfaces import IVersioning, VersioningError
from silva.translations import translate as _

empty_version = (None, None, None)


class RequestForApprovalInfo(object):
    """ simple helper class storing information about the
    current request for approval
    """

    def __init__(self):
        self.request_pending = None
        self.requester = None
        self.request_messages = []
        self.request_date = None

empty_request_for_approval_info = RequestForApprovalInfo()


class Versioning(object):
    """Mixin baseclass to make object contents versioned.
    """
    security = ClassSecurityInfo()

    implements(IVersioning)

    _unapproved_version = empty_version
    _approved_version = empty_version
    _public_version = empty_version
    _previous_versions = None
    _request_for_approval_info = empty_request_for_approval_info
    _first_publication_date = None

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'create_version')
    def create_version(self, version_id,
                       publication_datetime,
                       expiration_datetime):
        """Add unapproved version
        """
        self._update_publication_status()
        if self._approved_version != empty_version:
            msg = _(
                'There is an approved version already; unapprove it. (${id})',
                mapping={'id': self._approved_version[0]})
            raise VersioningError, msg
        if self._unapproved_version != empty_version:
            msg = _('There already is an unapproved version (${id}).',
                    mapping={'id': self._unapproved_version[0]})
            raise VersioningError, msg
        # if a version with this name already exists, complain
        if (self._public_version and
            version_id == self._public_version[0]):
            msg = _('The public version has that id already (${id}).',
                    mapping={'id': self._public_version[0]})
            raise VersioningError, msg
        previous_versions = self._previous_versions or []
        for previous_version in previous_versions:
            if version_id == previous_version[0]:
                msg = _('A previous version has that id already (${id}).',
                        {'id': self._previous_version[0]})
                raise VersioningError, msg

        self._unapproved_version = (version_id,
                                    publication_datetime,
                                    expiration_datetime)
        # overwrite possible previous info ...
        self._request_for_approval_info = RequestForApprovalInfo()
        self._index_version(self._unapproved_version[0])

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'approve_version')
    def approve_version(self):
        """Aprove the current unapproved version.
        """
        self._update_publication_status()
        if self._unapproved_version == empty_version:
            raise VersioningError,\
                  _('There is no unapproved version to approve.')
        if self._approved_version != empty_version:
            raise VersioningError,\
                  _('There already is an approved version.')
        if self._unapproved_version[1] is None:
            raise VersioningError,\
                  _('Cannot approve version without publication datetime.')
        # turn any publication dates in the past into now
        # this is to avoid odd caching behavior
        if not self._unapproved_version[1].isFuture():
            publish_now = 1
            self._unapproved_version = (self._unapproved_version[0],
                                        DateTime(),
                                        self._unapproved_version[2])
        else:
            publish_now = 0
        self._approved_version = self._unapproved_version
        self._unapproved_version = empty_version
        if self._request_for_approval_info != empty_request_for_approval_info:
            self._request_for_approval_info.request_pending = None
            self._request_for_approval_info = self._request_for_approval_info

        notify(events.ContentApprovedEvent(
                getattr(self, self._approved_version[0]),
                self._get_editable_rfa_info()))

        # update publication status; we may be published by now
        # will take care of indexing
        if publish_now:
            self._update_publication_status()
        else:
            # otherwise simply reindex approved
            self._reindex_version(self._approved_version[0])

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'unapprove_version')
    def unapprove_version(self):
        """Unapprove an approved but not yet public version.
        """
        self._update_publication_status()
        if self._approved_version == empty_version:
            raise VersioningError,\
                  _('No approved version to unapprove.')
        if self._unapproved_version != empty_version:
            msg = _(('Should never happen: unapproved version ${unapproved} found while '
                   'approved version ${approved} exists at the same time.'),
                    mapping={'unapproved': self._unapproved_version[0],
                             'approved': self._approved_version[0]})
            raise VersioningError, msg
        self._unapproved_version = self._approved_version
        self._approved_version = empty_version
        notify(events.ContentUnApprovedEvent(
                getattr(self, self._unapproved_version[0]),
                self._get_editable_rfa_info()))

        self._reindex_version(self._unapproved_version[0])


    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'close_version')
    def close_version(self):
        """Close public version.
        """
        self._update_publication_status()
        if self._public_version == empty_version:
            raise VersioningError,\
                  _('No public version to close.')
        previous_versions = self._previous_versions or []
        previous_versions.append(self._public_version)
        self._public_version = empty_version
        self._previous_versions = previous_versions
        notify(events.ContentClosedEvent(
                getattr(self, self._previous_versions[-1][0])))

        # remove it from the catalog (if required)
        # this way the catalog only contains unapproved, approved
        # and public versions
        self._unindex_version(self._previous_versions[-1][0])

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'create_copy')
    def create_copy(self):
        """Create new version of public version.
        """
        if self.get_next_version() is not None:
            return
        # get id of public version to copy
        version_id_to_copy = self.get_public_version()
        # if there is no public version, get id of last closed version
        # (which should always be there)
        if version_id_to_copy is None:
            version_id_to_copy = self.get_last_closed_version()
            # there is no old version left!
            if version_id_to_copy is None:
                # FIXME: could create new empty version..
                raise  VersioningError, "Should never happen!"
        # copy published version
        new_version_id = self.get_new_version_id()
        # FIXME: this only works if versions are stored in a folder as
        # objects; factory function for VersionedContent objects should
        # create an initial version with name '0', too.
        self.manage_clone(getattr(self, version_id_to_copy), new_version_id)
        self.create_version(new_version_id, None, None)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_new_version_id')
    def get_new_version_id(self):
        """get_new_version_id is used when a new version will be created,
        to get a new unique id.  This may or may not change internal
        variables"""
        new_version_id = str(self._version_count)
        self._version_count = self._version_count + 1
        return str(new_version_id)

    def _get_editable_rfa_info(self):
        """ helper method: return the request for approval information,
        this creates a new one, if necessary; notifes Zope that this
        has changed in advance ... i.e. do not call this method
        if You do not want to change the information.
        """
        if self._request_for_approval_info == empty_request_for_approval_info:
            self._request_for_approval_info = RequestForApprovalInfo()
        else:
            # Zope should be notified that it has changed
            self._request_for_approval_info = self._request_for_approval_info
        return self._request_for_approval_info

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'request_version_approval')
    def request_version_approval(self, message):
        """Request approval for the current unapproved version
        Raises VersioningError, if there is no such version,
        or it is already approved.
        Returns None otherwise
        """
        # called implicitely: self._update_publication_status()
        if self.get_unapproved_version() is None:
            raise VersioningError,\
                  _('There is no unapproved version to request approval for.')

        if self.is_version_approval_requested():
            raise VersioningError,\
                  _('The version is already requested for approval.')

        info = self._get_editable_rfa_info()
        info.requester = getSecurityManager().getUser().getId()
        info.request_date = DateTime()
        info.request_pending=1
        self._set_approval_request_message(message)
        notify(events.ContentRequestApprovalEvent(
                getattr(self, self._unapproved_version[0]),
                self._get_editable_rfa_info()))


    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'withdraw_version_approval')
    def withdraw_version_approval(self, message):
        """Withdraw a previous request for approval
        Implementation should raise VersioningError, if the
        currently unapproved version has no request for approval yet,
        or if there is no unapproved version.
        """

        self._update_publication_status()
        if self.get_unapproved_version is None:
            raise VersioningError,\
                  _('There is no unapproved version to request approval for.')

        if not self.is_version_approval_requested():
            raise VersioningError,\
                  _('The version is not requested for approval.')
        info = self._get_editable_rfa_info()
        original_requester = info.requester
        info.requester = getSecurityManager().getUser().getId()
        info.request_pending=None
        self._set_approval_request_message(message)
        notify(events.ContentApprovalRequestCanceledEvent(
                getattr(self, self._unapproved_version[0]),
                self._get_editable_rfa_info(),
                original_requester))

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'reject_version_approval')
    def reject_version_approval(self, message):
        """Reject a previous request for approval
        Implementation should raise VersioningError, if the
        currently unapproved version has no request for approval yet,
        or if there is no unapproved version.
        """

        self._update_publication_status()
        if self.get_unapproved_version is None:
            raise VersioningError,\
                  _('There is no unapproved version to request approval for.')

        if not self.is_version_approval_requested():
            raise VersioningError,\
                  _('The version is not requested for approval.')
        info = self._get_editable_rfa_info()
        original_requester = info.requester
        info.requester = getSecurityManager().getUser().getId()
        info.request_pending=None

        self._set_approval_request_message(message)
        notify(events.ContentApprovalRequestRefusedEvent(
                getattr(self, self._unapproved_version[0]),
                original_requester))

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_unapproved_version_publication_datetime')
    def set_unapproved_version_publication_datetime(self, dt):
        """Set publication datetime for unapproved, or None for no
        publication at all yet.
        """
        if self._unapproved_version == empty_version:
            raise VersioningError,\
                  _('No unapproved version.')
        version_id, publication_datetime, expiration_datetime = \
                    self._unapproved_version
        self._unapproved_version = version_id, dt, expiration_datetime
        self._reindex_version(self._unapproved_version[0])

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_unapproved_version_expiration_datetime')
    def set_unapproved_version_expiration_datetime(self, dt):
        """Set expiration datetime, or None for no expiration.
        """
        if self._unapproved_version == empty_version:
            raise VersioningError,\
                  _('No unapproved version.')
        version_id, publication_datetime, expiration_datetime = \
                    self._unapproved_version
        self._unapproved_version = version_id, publication_datetime, dt
        self._reindex_version(self._unapproved_version[0])

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_approved_version_publication_datetime')
    def set_approved_version_publication_datetime(self, dt):
        """Set publication datetime for approved.
        """
        if self._approved_version == empty_version:
            raise VersioningError,\
                  _('No approved version.')
        if dt is None:
            raise VersioningError,\
                  _('Must specify publication datetime.')
        if not dt.isFuture():
            dt = DateTime()
        version_id, publication_datetime, expiration_datetime = \
                    self._approved_version
        self._approved_version = version_id, dt, expiration_datetime
        # Redundant reindex?
        self._reindex_version(self._approved_version[0])
        # may become published, update publication status
        self._update_publication_status()

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_approved_version_expiration_datetime')
    def set_approved_version_expiration_datetime(self, dt):
        """Set expiration datetime, or None for no expiration.
        """
        if self._approved_version == empty_version:
            raise VersioningError,\
                  _('No approved version.')
        version_id, publication_datetime, expiration_datetime = \
                    self._approved_version
        self._approved_version = version_id, publication_datetime, dt
        self._reindex_version(self._approved_version[0])

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'set_public_version_expiration_datetime')
    def set_public_version_expiration_datetime(self, dt):
        """Set expiration datetime, or None for no expiration.
        """
        if self._public_version == empty_version:
            raise VersioningError,\
                  _('No public version.')
        version_id, publication_datetime, expiration_datetime = \
            self._public_version
        self._public_version = version_id, publication_datetime, dt
        # Redundant reindex?
        self._reindex_version(self._public_version[0])
        # may become closed, update publication status
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
            self._reindex_version(self._approved_version[0])
        elif self._unapproved_version[0]:
            version_id, publication_datetime, expiration_datetime = \
                        self._unapproved_version
            self._unapproved_version = version_id, dt, expiration_datetime
            self._reindex_version(self._unapproved_version[0])
        else:
            raise VersioningError,\
                  _('No next version.')

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_next_version_expiration_datetime')
    def set_next_version_expiration_datetime(self, dt):
        """Set expiration datetime of next version.
        """
        if self._approved_version[0]:
            version_id, publication_datetime, expiration_datetime = \
                        self._approved_version
            self._approved_version = version_id, publication_datetime, dt
            self._reindex_version(self._approved_version[0])
        elif self._unapproved_version[0]:
            version_id, publication_datetime, expiration_datetime = \
                        self._unapproved_version
            self._unapproved_version = version_id, publication_datetime, dt
            self._reindex_version(self._unapproved_version[0])
        else:
            raise VersioningError,\
                  _('No next version.')

    def _set_approval_request_message(self, message):
        """Allows to add a message concerning the
        current request for approval.
        setting the currently approved message
        overwrites any previous message for this content.
        The implementation cleans the message
        if a new version is created.
        """
        # very weak check ... allows to call this method
        # before or after requesting approval, or the like.
        if self.get_next_version() is None:
            raise VersioningError, \
                  _("There is no version to add messages for.")

        info = self._get_editable_rfa_info()
        info.request_messages.append(message)

    def _update_publication_status(self):
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
                        getattr(self, self._public_version[0])))
                # unindex version (now last closed)
                self._unindex_version(self._public_version[0])
            self._public_version = self._approved_version
            if self._first_publication_date is None:
                self._first_publication_date = publication_datetime
            # unindex previously approved version
            self._unindex_version(self._approved_version[0])
            self._approved_version = empty_version
            notify(events.ContentPublishedEvent(
                    getattr(self, self._public_version[0])))
            # index approved version that is now public
            self._index_version(self._public_version[0])
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
                    getattr(self, self._previous_versions[-1][0])))
            # remove from index
            self._unindex_version(self._previous_versions[-1][0])

    # ACCESSORS

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_version_approved')
    def is_version_approved(self):
        """Check whether version is approved.
        """
        self._update_publication_status()
        return self._approved_version != empty_version

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_version_published')
    def is_version_published(self):
        """Check whether version is published.
        """
        self._update_publication_status()
        return self._public_version != empty_version


    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_version_approval_requested')
    def is_version_approval_requested(self):
        """Check if there exists an unapproved version
        which has a request for approval.
        """
        return self._request_for_approval_info.request_pending is not None

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_unapproved_version')
    def get_unapproved_version(self, update_status=1):
        """Get the unapproved version.
        """
        if update_status:
            self._update_publication_status()
        return self._unapproved_version[0]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_unapproved_version_data')
    def get_unapproved_version_data(self, update_status=1):
        """Get all the workflow data of the unapproved version.
        """
        if update_status:
            self._update_publication_status()
        return self._unapproved_version

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_unapproved_version_publication_datetime')
    def get_unapproved_version_publication_datetime(self, update_status=1):
        """Get publication datetime."""
        if update_status:
            self._update_publication_status()
        return self._unapproved_version[1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_unapproved_version_expiration_datetime')
    def get_unapproved_version_expiration_datetime(self, update_status=1):
        """Get version datetime."""
        if update_status:
            self._update_publication_status()
        return self._unapproved_version[2]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approved_version')
    def get_approved_version(self, update_status=1):
        """Get the approved version.
        """
        if update_status:
            self._update_publication_status()
        return self._approved_version[0]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approved_version_data')
    def get_approved_version_data(self, update_status=1):
        """Get all the workflow data of the approved version.
        """
        if update_status:
            self._update_publication_status()
        return self._approved_version

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approved_version_publication_datetime')
    def get_approved_version_publication_datetime(self, update_status=1):
        """Get publication datetime."""
        if update_status:
            self._update_publication_status()
        return self._approved_version[1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approved_version_expiration_datetime')
    def get_approved_version_expiration_datetime(self, update_status=1):
        """Get version datetime."""
        if update_status:
            self._update_publication_status()
        return self._approved_version[2]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version')
    def get_next_version(self, update_status=1):
        """Get either approved version if available, or unapproved
        version if not, or None if no next version.
        """
        if update_status:
            self._update_publication_status()
        return self._approved_version[0] or self._unapproved_version[0]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version_data')
    def get_next_version_data(self, update_status=1):
        """Get all workflow data of either approved version if available, or
        unapproved version if not, or None if no next version.
        """
        if update_status:
            self._update_publication_status()
        return self._approved_version or self._unapproved_version

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version_publication_datetime')
    def get_next_version_publication_datetime(self, update_status=1):
        """Get publication datetime."""
        if update_status:
            self._update_publication_status()
        return self._approved_version[1] or self._unapproved_version[1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version_expiration_datetime')
    def get_next_version_expiration_datetime(self, update_status=1):
        """Get version datetime."""
        if update_status:
            self._update_publication_status()
        return self._approved_version[2] or self._unapproved_version[2]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version_status')
    def get_next_version_status(self):
        """Get status of next version.
        """
        # XXX i18n - should we translate these?
        if self.get_unapproved_version() is not None:
            if self.is_version_approval_requested():
                return "request_pending"
            else:
                return "not_approved"
        elif self.get_approved_version() is not None:
            return "approved"
        else:
            return "no_next_version"

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_public_version')
    def get_public_version(self, update_status=1):
        """Get the public version.
        """
        if update_status:
            self._update_publication_status()
        return self._public_version[0]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_public_version_data')
    def get_public_version_data(self, update_status=1):
        """Get all workflow data of the public version.
        """
        if update_status:
            self._update_publication_status()
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
    def get_public_version_publication_datetime(self, update_status=1):
        """Get publication datetime."""
        if update_status:
            self._update_publication_status()
        return self._public_version[1]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_public_version_expiration_datetime')
    def get_public_version_expiration_datetime(self, update_status=1):
        """Get version datetime."""
        if update_status:
            self._update_publication_status()
        return self._public_version[2]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_public_version_status')
    def get_public_version_status(self):
        if self.get_public_version() is not None:
            return "published"
        elif self.get_previous_versions():
            return "closed"
        else:
            return "no_public_version"

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_previous_versions')
    def get_previous_versions(self):
        """Get list of previous versions, index 0 most recent.
        """
        if self._previous_versions is None:
            return []
        else:
            return [version[0] for version in self._previous_versions]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_previous_versions_data')
    def get_previous_versions_data(self):
        """Get list of workflow data of the previous versions, index 0 most
        recent.
        """
        if self._previous_versions is None:
            return []
        else:
            return [version for version in self._previous_versions]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_last_closed_version')
    def get_last_closed_version(self, update_status=1):
        """Get the last closed version or None if no such thing.
        """
        if update_status:
            self._update_publication_status()
        versions = self.get_previous_versions()
        if len(versions) < 1:
            return None
        else:
            return versions[-1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approval_requester')
    def get_approval_requester(self):
        """Return the id of the user requesting approval
        of the currently unapproved version."""
        return self._request_for_approval_info.requester

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approval_requester')
    def get_approval_request_message(self):
        """Get the current message associated with
        request for approval; i.e. argument passed as message
        on the last change to the approval status
        ({request,withdraw,reject}_version_approval, or approve_version)
        May be None, if there is currently no such message.
        """
        messages = self._request_for_approval_info.request_messages
        if len(messages)==0:
            return None
        else:
            return messages[-1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approval_requester')
    def get_approval_request_datetime(self):
        """Get the date when the currently unapproved version
        did get a request for approval as a DateTime object,
        or None if there is no such version or request.
        """
        return self._request_for_approval_info.request_date

    def _index_version(self, version):
        pass

    def _reindex_version(self, version):
        pass

    def _unindex_version(self, version):
        pass


InitializeClass(Versioning)



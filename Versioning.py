# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.16 $
# Zope
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
import ExtensionClass
# Silva interfaces
from IVersioning import IVersioning
from IPublishable import IPublishable
# Silva
import SilvaPermissions

class VersioningError(Exception):
    pass

empty_version = (None, None, None)

class RequestForApprovalInfo:
    """ simple helper class storing information about the
    current request for approval
    """

    def __init__(self):
        self.request_pending = None
        self.requester = None
        self.request_messages = []
        self.request_date = None

empty_request_for_approval_info = RequestForApprovalInfo()

class Versioning:
    """Mixin baseclass to make object contents versioned.
    """
    security = ClassSecurityInfo()

    __implements__ = IVersioning
    
    _unapproved_version = empty_version
    _approved_version = empty_version
    _public_version = empty_version
    _previous_versions = None
    _request_for_approval_info = empty_request_for_approval_info
    
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
            raise VersioningError,\
                  'There is an approved version already; unapprove it. (%s)' %\
                  (self._approved_version[0])
        if self._unapproved_version != empty_version:
            raise VersioningError,\
                  'There already is an unapproved version (%s).' %\
                  (self._unapproved_version[0])
        # if a version with this name already exists, complain
        if (self._public_version and
            version_id == self._public_version[0]):
            raise VersioningError,\
                  'The public version has that id already (%s).' %\
                 (self._public_version[0])
        previous_versions = self._previous_versions or []
        for previous_version in previous_versions:
            if version_id == previous_version[0]:
                raise VersioningError,\
                      'A previous version has that id already (%s).' %\
                      (self._previous_version[0])
    
        self._unapproved_version = (version_id,
                                    publication_datetime,
                                    expiration_datetime)
        # overwrite possible previous info ...
        self._request_for_approval_info = RequestForApprovalInfo()
        self._reindex_version(self._unapproved_version)
        
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'approve_version')
    def approve_version(self):
        """Aprove the current unapproved version.
        """
        self._update_publication_status()
        if self._unapproved_version == empty_version:
            raise VersioningError,\
                  'There is no unapproved version to approve.'
        if self._approved_version != empty_version:
            raise VersioningError,\
                  'There already is an approved version.'
        if self._unapproved_version[1] is None:
            raise VersioningError,\
                  'Cannot approve version without publication datetime.'
        if IPublishable.isImplementedBy(self):
            if not self.can_approve():
                raise VersioningError,\
                      'Cannot approve version; not allowed.'
        self._approved_version = self._unapproved_version
        self._unapproved_version = empty_version
        if self._request_for_approval_info != empty_request_for_approval_info:
            self._request_for_approval_info.request_pending = None
            self._request_for_approval_info = self._request_for_approval_info
        self._reindex_version(self._approved_version)
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'unapprove_version')
    def unapprove_version(self):
        """Unapprove an approved but not yet public version.
        """
        self._update_publication_status()
        if self._approved_version == empty_version:
            raise VersioningError,\
                  'No approved version to unapprove.'
        if self._unapproved_version != empty_version:
            raise VersioningError,\
                  ('Should never happen: unapproved version %s found while '
                   'approved version %s exists at the same time.') % (self._unapproved_version[0],
                                                                      self._approved_version[0])        
        self._unapproved_version = self._approved_version
        self._approved_version = empty_version
        self._reindex_version(self._unapproved_version)
        
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'close_version')
    def close_version(self):
        """Close public version.
        """
        self._update_publication_status()
        if self._public_version == empty_version:
            raise VersioningError,\
                  'No public version to close.'
        previous_versions = self._previous_versions or []
        if previous_versions:
            last_closed_version = previous_versions[-1]
        else:
            last_closed_version = empty_version            
        previous_versions.append(self._public_version)
        self._public_version = empty_version
        self._previous_versions = previous_versions
        self._reindex_version(last_closed_version)
        self._reindex_version(previous_versions[-1])


    def _get_editeable_rfa_info(self):
        """ helper method: return the request for approval information,
        this creates a new one, if necessary; notifes Zope that this has changed
        in advance ... i.e. do not call this method if You do not want to change
        the information.
        """
        if self._request_for_approval_info == empty_request_for_approval_info:
            self._request_for_approval_info =  RequestForApprovalInfo()
        else:
            # Zope should be notified that it has changed
            self._request_for_approval_info = self._request_for_approval_info
        return self._request_for_approval_info
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'request_version_approval')
    def request_version_approval(self):
        """Request approval for the current unapproved version
        Raises VersioningError, if there is no such version, or it is already approved.
        Returns None otherwise
        """
        # called implicitely: self._update_publication_status()
        if self.get_unapproved_version() is None:
            raise VersioningError,\
                  'There is no unapproved version to request approval for.'

        if self.is_version_approval_requested():
            raise VersioningError,\
                  'The version is already requested for approval.'

        info = self._get_editeable_rfa_info()
        info.requester = self.REQUEST.AUTHENTICATED_USER.getUserName()
        info.request_date = DateTime()
        info.request_pending=1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'withdraw_version_approval')
    def withdraw_version_approval(self):
        """Withdraw a previous request for approval
        Implementation should raise VersioningError, if the
        currently unapproved version has no request for approval yet,
        or if there is no unapproved version.
        """
        
        self._update_publication_status()
        if self.get_unapproved_version is None:
            raise VersioningError,\
                  'There is no unapproved version to request approval for.'

        if not self.is_version_approval_requested():
            raise VersioningError,\
                  'The version is not requested for approval.'
        info = self._get_editeable_rfa_info()
        info.requester = self.REQUEST.AUTHENTICATED_USER.getUserName()
        info.request_pending=None
    

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_unapproved_version_publication_datetime')
    def set_unapproved_version_publication_datetime(self, dt):
        """Set publication datetime for unapproved, or None for no
        publication at all yet.
        """
        if self._unapproved_version == empty_version:
            raise VersioningError,\
                  'No unapproved version.'
        version_id, publication_datetime, expiration_datetime = self._unapproved_version
        self._unapproved_version = version_id, dt, expiration_datetime
        self._reindex_version(self._unapproved_version)
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_unapproved_version_expiration_datetime')
    def set_unapproved_version_expiration_datetime(self, dt):
        """Set expiration datetime, or None for no expiration.
        """
        if self._unapproved_version == empty_version:
            raise VersioningError,\
                  'No unapproved version.'
        version_id, publication_datetime, expiration_datetime = self._unapproved_version
        self._unapproved_version = version_id, publication_datetime, dt
        self._reindex_version(self._unapproved_version)
        
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_approved_version_publication_datetime')
    def set_approved_version_publication_datetime(self, dt):
        """Set publication datetime for approved.
        """
        if self._approved_version == empty_version:
            raise VersioningError,\
                  'No approved version.'
        if dt is None:
            raise VersioningError,\
                  'Must specify publication datetime.'
        version_id, publication_datetime, expiration_datetime = self._approved_version
        self._approved_version = version_id, dt, expiration_datetime
        self._reindex_version(self._approved_version)
        
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_approved_version_expiration_datetime')
    def set_approved_version_expiration_datetime(self, dt):
        """Set expiration datetime, or None for no expiration.
        """
        if self._approved_version == empty_version:
            raise VersioningError,\
                  'No approved version.'
        version_id, publication_datetime, expiration_datetime = self._approved_version
        self._approved_version = version_id, publication_datetime, dt
        self._reindex_version(self._approved_version)
        
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_next_version_publication_datetime')
    def set_next_version_publication_datetime(self, dt):
        """Set publication datetime of next version.
        """
        if self._approved_version[0]:
            version_id, publication_datetime, expiration_datetime = self._approved_version
            self._approved_version = version_id, dt, expiration_datetime
            self._reindex_version(self._approved_version)
        elif self._unapproved_version[0]:
            version_id, publication_datetime, expiration_datetime = self._unapproved_version
            self._unapproved_version = version_id, dt, expiration_datetime
            self._reindex_version(self._unapproved_version)
        else:
            raise VersioningError,\
                  'No next version.'
            
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_next_version_expiration_datetime')
    def set_next_version_expiration_datetime(self, dt):
        """Set expiration datetime of next version.
        """
        if self._approved_version[0]:
            version_id, publication_datetime, expiration_datetime = self._approved_version
            self._approved_version = version_id, publication_datetime, dt
            self._reindex_version(self._approved_version)
        elif self._unapproved_version[0]:
            version_id, publication_datetime, expiration_datetime = self._unapproved_version
            self._unapproved_version = version_id, publication_datetime, dt
            self._reindex_version(self._unapproved_version)
        else:
            raise VersioningError,\
                  'No next version.'

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_approval_request_message')
    def set_approval_request_message(self, message):
        """Allows to add a message concerning the
        current request for approval.
        setting the currently approved message
        overwrites any previous message for this content.
        The implementation cleans the message
        if a new version is created.
        """
        # very weak restriction ... allows to call this method
        # before or after requesting approval, or the like.
        if self.get_next_version() is None:
            raise VersioningError, \
                  "There is no version to add messages for."
        
        info = self._get_editeable_rfa_info()
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
                    last_closed_version = empty_version
                else:
                    last_closed_version = self._previous_versions[-1]
                self._previous_versions.append(self._public_version)
                # reindex version (now last closed)
                self._reindex_version(self._public_version)
                # reindex previously last_closed_version
                if last_closed_version is not empty_version:
                    self._reindex_version(last_closed_version)
            self._public_version = self._approved_version
            self._approved_version = empty_version
            # reindex approved version that is now public
            self._reindex_version(self._public_version)
        # get expiration datetime of public version 
        expiration_datetime = self._public_version[2]
        # expire public version if expiration datetime reached
        if expiration_datetime and now >= expiration_datetime:
            # make sure to add it to the previous versions
            previous_versions = self._previous_versions or []
            if previous_versions:
                last_closed_version = self._previous_versions[-1]
            else:
                last_closed_version = empty_version
            previous_versions.append(self._public_version)
            self._public_version = empty_version
            self._previous_versions = previous_versions
            # reindex last closed and now newly last closed version
            self._reindex_version(last_closed_version)
            self._reindex_version(self._previous_versions[-1])
            
    # ACCESSORS

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_version_approved')
    def is_version_approved(self):
        """Check whether version is approved.
        """
        self._update_publication_status()
        return self._approved_version != empty_version

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
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
    def get_unapproved_version(self):
        """Get the unapproved version.
        """
        self._update_publication_status()
        return self._unapproved_version[0]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_unapproved_version_publication_datetime')
    def get_unapproved_version_publication_datetime(self):
        """Get publication datetime."""
        self._update_publication_status()
        return self._unapproved_version[1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_unapproved_version_expiration_datetime')
    def get_unapproved_version_expiration_datetime(self):
        """Get version datetime."""
        self._update_publication_status()
        return self._unapproved_version[2]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approved_version')
    def get_approved_version(self):
        """Get the approved version.
        """
        self._update_publication_status()
        return self._approved_version[0]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approved_version_publication_datetime')
    def get_approved_version_publication_datetime(self):
        """Get publication datetime."""
        self._update_publication_status()
        return self._approved_version[1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_approved_version_expiration_datetime')
    def get_approved_version_expiration_datetime(self):
        """Get version datetime."""
        self._update_publication_status()
        return self._approved_version[2]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version')
    def get_next_version(self):
        """Get either approved version if available, or unapproved
        version if not, or None if no next version.
        """
        self._update_publication_status()
        return self._approved_version[0] or self._unapproved_version[0]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version_publication_datetime')
    def get_next_version_publication_datetime(self):
        """Get publication datetime."""
        self._update_publication_status()
        return self._approved_version[1] or self._unapproved_version[1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version_expiration_datetime')
    def get_next_version_expiration_datetime(self):
        """Get version datetime."""
        self._update_publication_status()
        return self._approved_version[2] or self._unapproved_version[2]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_next_version_status')
    def get_next_version_status(self):
        """Get status of next version.
        """
        if self.get_unapproved_version() is not None:
            if self.is_version_approval_requested():
                return "request_pending"
            else:
                return "not_approved"
        elif self.get_approved_version() is not None:
            return "approved"
        else:
            return "no_next_version"

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_public_version')
    def get_public_version(self):
        """Get the public version.
        """
        self._update_publication_status()
        return self._public_version[0]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_public_version_publication_datetime')
    def get_public_version_publication_datetime(self):
        """Get publication datetime."""
        self._update_publication_status()
        return self._public_version[1]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_public_version_expiration_datetime')
    def get_public_version_expiration_datetime(self):
        """Get version datetime."""
        self._update_publication_status()
        return self._public_version[2]

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
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
                              'get_last_closed_version')
    def get_last_closed_version(self):
        """Get the last closed version or None if no such thing.
        """
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
        request for approval; i.e. argument passed the
        on the last call to "set_approval_request_message".
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

    def _reindex_version(self, version):
        pass
        
InitializeClass(Versioning)




# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
import Interface

class IVersioning(Interface.Base):
    """Can be mixed in with an object to support simple versioning.
    This interface only keeps a reference id to the version and the
    various datetimes. The versioned objects themselves are not
    managed by this interface (see VersionedContent instead).
    """

    # MANIPULATORS
    def create_version(version_id,
                       publication_datetime,
                       expiration_datetime):
        """Add unapproved version.
        """
        pass

    def approve_version():
        """Approve the current unapproved version.
        """
        pass

    def unapprove_version():
        """Unapproved an approved but not yet published version.
        """
        pass

    def close_version():
        """Close the public version.
        """
        pass


    def request_version_approval():
        """Request approval for the current unapproved version
        Implementation should raise VersioningError, if there
        is no such version.
        Returns None otherwise
        """
        pass

    def withdraw_version_approval():
        """Withdraw a previous request for approval
        Implementation should raise VersioningError, if the
        currently unapproved version has no request for approval yet,
        or if there is no unapproved version.
        """
        pass

    
    def set_unapproved_version_publication_datetime(dt):
        """Set the publicationd datetime for the unapproved version,
        or None if this is not yet known.
        """
        pass
    
    def set_unapproved_version_expiration_datetime(dt):
        """Set the expiration datetime of the unapproved version,
        or None if it never expires.
        """
        pass
    
    def set_approved_version_publication_datetime(dt):
        """Change the publication datetime for the approved version.
        """
        pass

    def set_approved_version_expiration_datetime(dt):
        """Change the expiration datetime for the approved version, or
        None if there is no expiration.
        """
        pass

    def set_approval_request_message(message):
        """Allows to add a message concerning the
        current request for approval.
        setting the currently approved message
        overwrites any previous message for this content.
        The implementation may clean the message
        after the content is approved.
        """
        pass
    
    
    # ACCESSORS

    def is_version_approved():
        """Check whether there exists an approved version.
        """
        pass

    def is_version_published():
        """Check whether there exists a published version.
        """
        pass

    def is_version_approval_requested():
        """Check if there exists an unapproved version
        which has a request for approval.
        """
        pass
    
    
    def get_unapproved_version():
        """Get the id of the unapproved version.
        """
        pass

    def get_unapproved_version_publication_datetime():
        """Get the publication datetime for the unapproved version,
        or None if no publication datetime yet.
        """
        pass
    
    def get_unapproved_version_expiration_datetime():
        """Get the expiration datetime for the unapproved version,
        or None if no publication datetime yet.
        """
        pass

    def get_approved_version():
        """Get the id of the approved version.
        """
        pass

    def get_approved_version_publication_datetime():
        """Get the publication of the approved version.
        """
        pass

    def get_approved_version_expiration_datetime():
        """Get the expiration datetime for the approved version,
        or None if no expiration datetime yet.
        """
        pass

    def get_next_version():
        """Get the id of the next version. This is the approved version
        if available, or the unapproved version otherwise, or None if
        there is no next version at all.
        """
        pass

    def get_next_version_publication_datetime():
        """Get the publication datetime of the next version, or None
        if no such datetime is known.
        """
        pass

    def get_next_version_expiration_datetime():
        """Get the expiration datetime of the next version, or None
        if there is no expiration datetime.
        """
        pass
    
    def get_next_version_status():
        """Get the status of the next version.
        Result can be 'not_approved', 'approved', or 'no_next_version'.
        """
        pass

    def get_public_version():
        """Get the id of the public version.
        """
        pass

    def get_public_version_publication_datetime():
        """Get the publication datetime of the public version.
        """
        pass

    def get_public_version_expiration_datetime():
        """Get the expiration datetime of the public version, or
        None if this version never expires.
        """
        pass

    def get_public_version_status():
        """Get the status of the published version.
        Result can be 'published', 'closed', or 'no_public_version'
        """
        pass

    def get_previous_versions():
        """Get a list of the ids of the most recent versions (that
        are not public anymore. Index 0 is oldest, up is more recent
        versions).
        """
        pass

    def get_last_closed_version():
        """Get the id of the version that was last closed, or None if
        no such version.
        """
        pass

    def get_approval_requester():
        """Return the id of the user requesting approval
        of the currently unapproved version.
        XXX fishy: If the request for approval is withdrawn/rejected,
        this returns the user id of the one having
        withdrawn/rejected the request.
        (Maybe write another method for this?)
        """
        pass
    
    def get_approval_request_message():
        """Get the current message associated with
        request for approval; i.e. argument passed the
        on the last call to "set_approval_request_message".
        May return None if there is no such message or
        the message has been purged by an approval.
        """
        pass

    def get_approval_request_datetime():
        """Get the date when the currently unapproved version
        did get a request for approval as a DateTime object,
        or None if there is no such version or request.
        """
        pass
    
    def can_approve():
        """Returns true if approval is allowed.
        """
        pass

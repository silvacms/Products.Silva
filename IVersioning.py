# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
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

    
    # ACCESSORS

    def is_version_approved():
        """Check whether there exists an approved version.
        """
        pass

    def is_version_published():
        """Check whether there exists a published version.
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
    
    def can_approve():
        """Returns true if approval is allowed.
        """
        pass

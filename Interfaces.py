import Interface

class SilvaObject(Interface.Base):
    """Interface that should be supported by all Silva objects.
    """
    # MANIPULATORS
    def set_title(self):
        """Change the title of the content object.
        """
        pass

    # MANIPULATORS
    def manage_afterAdd(self, item, container):
        """Hook called by Zope just after the item was added to
        container. Adds item id to an ordered list, if item is
        a publishable object.
        """
        pass

    def manage_beforeDelete(self, item, container):
        """Hook called by Zope just before the item is deleted from
        container. Removes item id to from ordered list (item is
        a publishable object).
        """
        pass        

    # ACCESSORS
    def title(self):
        """The title of the content object.
        """
        pass

    def get_creation_datetime(self):
        """Creation datetime of the object. Return None if not supported.
        """
        pass

    def get_modification_datetime(self):
        """Last modification datetime of the object. Return None if not
        supported.
        """
        pass

    def get_editable(self):
        """Get the editable version (may be object itself if no versioning).
        Returns None if there is no such version.
        """
        pass

    def get_previewable(self):
        """Get the previewable version (may be the object itself if no
        versioning).
        Returns None if there is no such version.
        """
        pass

    def get_viewable(self):
        """Get the publically viewable version (may be the object itself if
        no versioning).
        Returns None if there is no such version.
        """
        pass

class Publishable(Interface.Base):
    # MANIPULATORS
    def activate(self):
        """Make this publishable item active.
        """
        pass

    def deactivate(self):
        """Deactivate publishable item.
        """
        pass
    
    # ACCESSORS
    def is_published(self):
        """Return true if this object is visible to the public.
        """
        pass

    def is_active(self):
        """Returns true if this object is actually active and
        in the table of contents.
        """
        pass

    def can_activate(self):
        pass

    def can_deactivate(self):
        pass
    
class Asset(SilvaObject):
    """An object that does not appear in the publication's
    table of content directly.
    """
    pass

class Content(SilvaObject, Publishable):
    """An object that can be published directly and would appear
    in the table of contents. Can be ordered.
    """
    # ACCESSORS
    def get_content(self):
        """Used by acquisition to get the nearest containing content object.
        """
        pass

    def content_url(self):
        """Used by acquisition to get the URL of the containing content object.
        """
        pass
    
    def is_default(self):
        """True if this content object is the default content object of
        the folder.
        """
        pass


class Container(SilvaObject, Publishable):
    
    # MANIPULATORS
    def move_object_up(self, id):
        """Move object with id up in the list of ordered publishables.
        Return true in case of success.
        """
        pass

    def move_object_down(self, id):
        """Move object with id down in the list of ordered publishables.
        Return true in case of success.
        """
        pass

    def move_to(self, move_ids, index):
        """Move ids just before index.
        Return true in case success.
        """
        pass
    
    # cut copy paste?
    
    # ACCESSORS

    def get_container(self):
        """Get the nearest container in the acquisition hierarchy.
        (this one)
        """
        pass

    def container_url(self):
        """Get the url of the nearest container.
        """
        pass
    
    def is_transparent(self):
        """Show this subtree in get_tree().
        """
        pass
    
    def get_default(self):
        """Get the default content object of the folder. If
        no default is available, return None.
        """
        pass

    def get_ordered_publishables(self):
        """Get list of active publishables of this folder, in
        order.
        """
        pass
    
    def get_nonactive_publishables(self):
        """Get a list of nonactive publishables. This is not in
        any fixed order.
        """
        pass
    
    def get_assets(self):
        """Get a list of non-publishable objects in this folder.
        (not in any order).
        """
        pass
    
    def get_tree(self):
        """Get flattened tree of all active publishables.
        This is a list of indent, object tuples.
        """
        pass

    def get_container_tree(self):
        """Get flattened tree of all sub-containers.
        This is a list of indent, object tuples.
        """
        pass
    
class Security(Interface.Base):
    """Can be mixed in with an object to support Silva security.
    (built on top of Zope security)
    """
    def get_users(self):
        """Get the users that have local roles here.
        """
        pass

    def get_groups(self):
        """Get the groups that have local roles here.
        """
        pass

    def get_roles_for_user(self, userid):
        """Get the local roles that a silva user has here.
        """
        pass

    def get_roles_for_group(self, groupid):
        """Get the local roles that a silva group has here.
        """
        pass

    def set_roles_for_user(self, userid, roles):
        pass

    def add_role_to_user(self, userid, role):
        pass

    def set_roles_for_group(self, userid, roles):
        pass

    def add_role_to_group(self, userid, role):
        pass
    
class Versioning(Interface.Base):
    """Can be mixed in with an object to support simple versioning.
    This interface only keeps a reference id to the version and the
    various datetimes. The versioned objects themselves are not
    managed by this interface (see VersionedContent instead).
    """

    # MANIPULATORS
    def create_version(self, version_id,
                       publication_datetime,
                       expiration_datetime):
        """Add unapproved version.
        """
        pass

    def approve_version(self):
        """Approve the current unapproved version.
        """
        pass

    def unapprove_version(self):
        """Unapproved an approved but not yet published version.
        """
        pass

    def close_version(self):
        """Close the public version.
        """
        pass
    
    def set_unapproved_version_publication_datetime(self, dt):
        """Set the publicationd datetime for the unapproved version,
        or None if this is not yet known.
        """
        pass
    
    def set_unapproved_version_expiration_datetime(self, dt):
        """Set the expiration datetime of the unapproved version,
        or None if it never expires.
        """
        pass
    
    def set_approved_version_publication_datetime(self, dt):
        """Change the publication datetime for the approved version.
        """
        pass

    def set_approved_version_expiration_datetime(self, dt):
        """Change the expiration datetime for the approved version, or
        None if there is no expiration.
        """
        pass

    
    # ACCESSORS

    def is_version_approved(self):
        """Check whether there exists an approved version.
        """
        pass

    def is_version_published(self):
        """Check whether there exists a published version.
        """
        pass
    
    def get_unapproved_version(self):
        """Get the id of the unapproved version.
        """
        pass

    def get_unapproved_version_publication_datetime(self):
        """Get the publication datetime for the unapproved version,
        or None if no publication datetime yet.
        """
        pass
    
    def get_unapproved_version_expiration_datetime(self):
        """Get the expiration datetime for the unapproved version,
        or None if no publication datetime yet.
        """
        pass

    def get_approved_version(self):
        """Get the id of the approved version.
        """
        pass

    def get_approved_version_publication_datetime(self):
        """Get the publication of the approved version.
        """
        pass

    def get_approved_version_expiration_datetime(self):
        """Get the expiration datetime for the approved version,
        or None if no expiration datetime yet.
        """
        pass

    def get_next_version(self):
        """Get the id of the next version. This is the approved version
        if available, or the unapproved version otherwise, or None if
        there is no next version at all.
        """
        pass

    def get_next_version_publication_datetime(self):
        """Get the publication datetime of the next version, or None
        if no such datetime is known.
        """
        pass

    def get_next_version_expiration_datetime(self):
        """Get the expiration datetime of the next version, or None
        if there is no expiration datetime.
        """
        pass
    
    def get_next_version_status(self):
        """Get the status of the next version.
        Result can be 'not_approved', 'approved', or 'no_next_version'.
        """
        pass

    def get_public_version(self):
        """Get the id of the public version.
        """
        pass

    def get_public_version_publication_datetime(self):
        """Get the publication datetime of the public version.
        """
        pass

    def get_public_version_expiration_datetime(self):
        """Get the expiration datetime of the public version, or
        None if this version never expires.
        """
        pass

    def get_public_version_status(self):
        """Get the status of the published version.
        Result can be 'published', 'closed', or 'no_public_version'
        """
        pass

    def get_previous_versions(self):
        """Get a list of the ids of the most recent versions (that
        are not public anymore. Index 0 is oldest, up is more recent
        versions).
        """
        pass

    def get_last_closed_version(self):
        """Get the id of the version that was last closed, or None if
        no such version.
        """
        pass
    
    def can_approve(self):
        """Returns true if approval is allowed.
        """
        pass
    
class VersionedContent(Versioning, Content):
    """This is a content object that is versioned. Presumed is that
    upon creation of the content object it is assigned a version id
    that is registered with the Versioning interface as the unapproved
    version.
    """
    
    # MANIPULATORS
    def create_copy(self):
        """Create a new copy of the public version. Automatically
        assign a new id for this copy and register this as the
        next version. If there is already a next version, this
        operation will fail.
        """
        pass

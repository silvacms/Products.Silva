import Interface

class SilvaObject(Interface.Base):
    """Interface that should be supported by all Silva objects.
    """
    # MANIPULATORS
    def set_title(self):
        """Change the title of the content object.
        """
        pass

    # ACCESSORS
    def title(self):
        """The title of the content object.
        """
        pass

    def is_published(self):
        """Return true if this object is visible to the public.
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

class Information(SilvaObject):
    """Information that does not appear in the official contents of a publication,
    but can be referred to from documents and can be included
    (images, contactinfo, etc)'
    """
    def editor(self):
        """
        """
        pass

    def preview(self):
        """See the information as the user would see it.
        """
        pass

    
    def view(self):
        """Use the information in context.
        """
        pass
    
class Content(SilvaObject):
    # MANIPULATORS

    
    # ACCESSORS    
    def editor(self):
        """Show the editor of the content object to the author.
         """
        pass

    def preview(self):
        """Show the content object to the author as if it's seen
        by the end user.
        """
        pass
    
    def view(self):
        """Show the content object to the end user.
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
        are not public anymore. Index 0 is most recent, up is older
        versions).
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
    
class Container(SilvaObject):
    
    # MANIPULATORS
    def move_object_up(self, id):
        """Move object with id up in the list of subobjects.
        """
        pass

    def move_object_down(self, id):
        """Move object with id down in the list of subobjects.
        """
        pass

    def move_object(self, id, index):
        """Move and insert object with id just before index.
        """
        pass

    # cut copy paste?
    
    # ACCESSORS
    
    def get_contents(self):
        """Get list of subobjects (in the right order).
        """
        pass

    def get_tree(self):
        """Get flattened tree of all subobjects.
        This is a list of indent, object tuples.
        """
        pass
    
class TransparentContainer(Container):
    """A container that is transparent in the sense that get_tree
    queries for subjects.
    """
    pass

class OpaqueContainer(Container):
    """A container that is opaque in the sense that get_tree doesn't
    query for subobjects, but stops.
    """
    pass


# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

"""This module contains interfaces declarations for Silva contents.
"""

from zope.interface import Interface, Attribute
from silva.core.layout.interfaces import ICustomizable
from grokcore.component.interfaces import IContext

class ISecurity(Interface):
    """Can be mixed in with an object to support Silva security.
    (built on top of Zope security)
    Methods prefixed with sec_ so as not to disrupt similarly named
    Zope's security methods. (ugly..)
    """
    # MANIPULATORS
    def sec_assign(userid, role):
        """Assign role to userid for this object.
        """
        pass

    def sec_remove(userid):
        """Remove a user completely from this object.
        """
        pass

    def sec_revoke(userid, revoke_roles):
        """Remove roles from user in this object.
        """
        pass

    def sec_create_lock():
        """Create lock for this object. Return true if successful.
        """

    # ACCESSORS

    def sec_is_locked():
        """Check whether this object is locked by a user currently
        editing.
        """

    def sec_have_management_rights():
        """Check whether we have management rights here.
        """

    def sec_get_userids():
        """Get the userids that have local roles here.
        """
        pass

    def sec_get_roles_for_userid(userid):
        """Get the local roles that a userid has here.
        """
        pass

    def sec_get_roles():
        """Get all roles defined here that we're interested in managing.
        """
        pass

    def sec_find_users(search_string):
        """Look up users in user database. Return a dictionary of
        users with userid as key, and dictionaries with user info
        as value.
        """
        pass

    def sec_get_member(userid):
        """Get member object for user id.
        """
        pass

    def sec_get_local_defined_userids():
        """Get the list of userids with locally defined roles, or None
        """
        pass

    def sec_get_local_roles_for_userid(userid):
        """Get a list of local roles that a userid has here, or None
        """
        pass

    def sec_get_upward_defined_userids():
        """Get the list of userids with roles defined in a higer
        level of the tree, or None
        """
        pass

    def sec_get_upward_roles_for_userid(userid):
        """Get the roles that a userid has here, defined in a higer
        level of the tree, or None
        """
        pass

    def sec_get_downward_defined_userids():
        """Get the list of userids with roles defined in a lower
        level of the tree (these users do not have rights on this
        local level), or None
        """
        pass

    def sec_get_local_defined_groups():
        """Get the list of groups with locally defined roles.
        """
        pass

    def sec_get_local_roles_for_group(group):
        """Get a list of local roles that are defined for a group here.
        """
        pass

    def sec_get_upward_defined_groups():
        """Get the list of groups with roles defined in a higer
        level of the tree.
        """
        pass

    def sec_get_upward_roles_for_group(group):
        """Get the roles that a group has here, defined in a higer
        level of the tree.
        """
        pass

    def sec_get_downward_defined_groups():
        """Get the list of groups with roles defined in a lower
        level of the tree.
        """
        pass

    def sec_get_last_author_info():
        """Get information about the last author of this object.
        This is *not* the last author of the public version of this
        object.
        """

class ISilvaObject(IContext, ISecurity, ICustomizable):
    """Interface that should be supported by all Silva objects.
    """
    # MANIPULATORS
    def set_title(title):
        """Change the title of the content object.
        """
        pass

    # ACCESSORS
    def get_title():
        """The title of the content object.
        PUBLIC
        """
        pass

    def get_title_or_id():
        """The title or id of the content object.
        PUBLIC
        """
        pass

    def get_creation_datetime():
        """Creation datetime of the object. Return None if not supported.
        PUBLIC
        """
        pass

    def get_modification_datetime():
        """Last modification datetime of the object. Return None if not
        supported.
        PUBLIC
        """
        pass

    def get_breadcrumbs():
        """Get the objects above this item, until the Silva Root, in
        order from Silva Root.
        PUBLIC
        """
        pass

    def get_editable():
        """Get the editable version (may be object itself if no versioning).
        Returns None if there is no such version.
        """
        pass

    def get_previewable():
        """Get the previewable version (may be the object itself if no
        versioning).
        Returns None if there is no such version.
        """
        pass

    def get_viewable():
        """Get the publically viewable version (may be the object itself if
        no versioning).
        Returns None if there is no such version.
        """
        pass

    def preview():
        """Render this object using the public view defined in the view registry.
        This should use methods on the object itself and the version object
        obtained by get_previewable() to render the object to HTML.
        """
        pass

    def view():
        """Render this object using the public view defined in the view registry.
        This should use methods on the object itself and the version object
        obtained by get_viewable() to render the object to HTML.
        PUBLIC
        """
        pass


    # This should be only in a view code ?

    def implements_publishable():
        """This object implements IPublishable."""

    def implements_asset():
        """This object implements IAsset."""

    def implements_content():
        """This object implements IContent."""

    def implements_container():
        """This object implements IContainer."""

    def implements_publication():
        """This object implements IPublication."""

    def implements_root():
        """This object implements IRoot."""

    def implements_versioned_content():
        """This object implements IVersionedContent."""

    def is_deletable():
        """Returns True if object is deletable right now
        """


class IPublishable(Interface):
    # MANIPULATORS

    # ACCESSORS
    def is_published():
        """Return true if this object is visible to the public.
        PUBLIC
        """
        pass

    def is_approved():
        """Return true if this object is versioned or contains
        versioned content that is approved.
        """
        pass


###############################################################
### Container
###############################################################

class IContainer(ISilvaObject, IPublishable):

    used_space = Attribute(u"Used space by assets.")

    # MANIPULATORS
    def move_object_up(id):
        """Move object with id up in the list of ordered publishables.
        Return true in case of success.
        """
        pass

    def move_object_down(id):
        """Move object with id down in the list of ordered publishables.
        Return true in case of success.
        """
        pass

    def move_to(move_ids, index):
        """Move ids just before index.
        Return true in case success.
        """
        pass

    def action_rename(orig_id, new_id):
        """Rename subobject with orig_id into new_id.
        Cannot rename approved or published content.
        """
        pass

    def action_delete(ids):
        """Delete ids in this container.
        Cannot delete approved or published content.
        """
        pass

    def action_cut(ids, REQUEST):
        """Cut ids in this folder, putting them on clipboard in REQUEST.
        Cannot cut approved or published content.
        """
        pass

    def action_copy(ids, REQUEST):
        """Copy ids in this folder, putting them on clipboard in REQUEST.
        """
        pass

    def action_paste(REQUEST):
        """Paste clipboard to this folder.
        After paste, approved or published content is automatically
        unapproved and/or closed.
        """
        pass


    def update_quota(self, delta):
        """
        Update used space, and verify quota for this folder.
        """
        pass


    # ACCESSORS
    def get_silva_addables():
        """Get a list of meta_type_dicts (from filtered_meta_types()) that
        are addable to this container.
        """
        pass

    def get_silva_addables_all():
        """Get a list of meta_types of all addables that exist in
        Silva.
        """

    def get_silva_addables_allowed():
        """Gives a list of all meta_types that are explicitly allowed here.
        """

    def get_container():
        """Get the nearest container in the acquisition hierarchy.
        (this one)
        PUBLIC
        """
        pass

    def container_url():
        """Get the url of the nearest container.
        PUBLIC
        """
        pass

    def is_transparent():
        """Show this subtree in get_tree().
        PUBLIC
        """
        pass

    def is_delete_allowed(id):
        """Return true if subobject with name 'id' can be deleted.
        This is only allowed if the subobject is not published or
        approved.
        """
        pass

    def get_default():
        """Get the default content object of the folder. If
        no default is available, return None.
        PUBLIC
        """
        pass

    def get_ordered_publishables():
        """Get list of active publishables of this folder, in
        order.
        """
        pass

    def get_nonactive_publishables():
        """Get a list of nonactive publishables. This is not in
        any fixed order.
        """
        pass

    def get_assets():
        """Get a list of assets objects in this folder.  (not in any
        fixed order).

        PUBLIC
        """
        pass

    def get_non_publishables():
        """Get a list of non-publishable objects in this folder. (not
        in any fixed order) Includes assets, configuration objects and
        anything else that is not a publishable.

        PUBLIC
        """
        pass

    def get_assets_of_type(meta_type):
        """Get list of assets of a certain meta_type.
        PUBLIC
        """
        pass

    def get_tree():
        """Get flattened tree of all active publishables.
        This is a list of indent, object tuples.
        """
        pass

    def get_container_tree():
        """Get flattened tree of all sub-containers.
        This is a list of indent, object tuples.
        PUBLIC
        """
        pass

    def get_public_tree():
        """Get tree of all publishables that are public.
        and not hidden from tocs
        PUBLIC
        """
        pass

    def get_public_tree_all():
        """Get tree of all publishables that are public,
        and not hidden from tocs
        including the publishables in subpublications.
        PUBLIC
        """
        pass

    def get_status_tree():
        """Get tree of all active content objects. For containers,
        show the default object if available.
        """
        pass

class IFolder(IContainer):
    """Basic Silva Folder.
    """


class IPublication(IContainer):
    """An interface supported by publication objects.
    """

    def set_silva_addables_allowed_in_publication(addables):
        """Set the list of addables explicitly allowed in this publication.
        If 'addables' is set to None the list is acquired from the
        publication higher in the hierarchy. If this is the root,
        return the complete list.
        """

    def get_silva_addables_allowed_in_publication():
        """Get a list of all addables explicitly allowed in this
        publication (and its subcontainers).
        """

    def is_silva_addables_acquired():
        """Return true if the list of addables is acquired from
        above (set_silva_addables_allowed_in_publication set to None), false
        if not.
        """

class IRoot(IPublication):
    """An interface supported by Silva root objects.
    """

    def get_root():
        """Get root of site. Can be used with acquisition get the
        'nearest' Silva root.
        """
        pass

    def add_silva_addable_forbidden(meta_type):
        """Forbid use of meta_type in SMI. The meta_type won't show
        up anymore, including in the publication metadata tab where
        individual items can be disabled for particular publications.
        """

    def clear_silva_addables_forbidden():
        """Clear any forbidden addables. All addables show up in the
        SMI again.
        """

    def is_silva_addable_forbidden(meta_type):
        """Returns true if meta_type should not show up in the SMI.
        """

###############################################################
### Content
###############################################################

class IContent(ISilvaObject, IPublishable):
    """An object that can be published directly and would appear
    in the table of contents. Can be ordered.
    """
    # ACCESSORS
    def get_content():
        """Used by acquisition to get the nearest containing content object.
        PUBLIC
        """
        pass

    def is_cacheable():
        """Return true if the public view of this object can be safely cached.
        This means the public view should not contain any dynamically
        generated content.
        """

    def content_url():
        """Used by acquisition to get the URL of the containing content object.
        PUBLIC
        """
        pass

    def is_default():
        """True if this content object is the default content object of
        the folder.
        PUBLIC
        """
        pass


class IAutoTOC(IContent):
    pass


###############################################################
### Versioned content
###############################################################

class IVersioning(Interface):
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


    def request_version_approval(self, message):
        """Request approval for the current unapproved version
        Implementation should raise VersioningError, if there
        is no such version.
        Returns None otherwise
        """
        pass

    def withdraw_version_approval(self, message):
        """Withdraw a previous request for approval
        Implementation should raise VersioningError, if the
        currently unapproved version has no request for approval yet,
        or if there is no unapproved version.
        """
        pass

    def reject_version_approval(self, message):
        """Reject a request for approval made by some Author
        Implementation should raise VersioningError, if the
        currently unapproved version has no request for approval yet,
        or if there is no unapproved version.
        One need to have the ApproveSilvaContent permission to call
        this method
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
        PUBLIC
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

    def get_first_publication_date(self):
        """Get the earliest publication date of any version of this Content.
        Needed for rss/atom feeds.
        """

    def get_public_version_publication_datetime():
        """Get the publication datetime of the public version.
        PUBLIC
        """
        pass

    def get_public_version_expiration_datetime():
        """Get the expiration datetime of the public version, or
        None if this version never expires.
        PUBLIC
        """
        pass

    def get_public_version_status():
        """Get the status of the published version.
        Result can be 'published', 'closed', or 'no_public_version'
        PUBLIC
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

class IVersionedContent(IVersioning, IContent):
    """This is a content object that is versioned. Presumed is that
    upon creation of the content object it is assigned a version id
    that is registered with the Versioning interface as the unapproved
    version.
    """

    # MANIPULATORS
    def create_copy():
        """Create a new copy of the public version. Automatically
        assign a new id for this copy and register this as the
        next version. If there is already a next version, this
        operation will fail.
        """
        pass

class ICatalogedVersionedContent(IVersionedContent):
    """Content object that is also in the catalog.
    """
    def indexVersions():
        """Reindex with catalog all the versions that need to be indexed.
        """

    def unindexVersions():
        """Unindex all versions.
        """

    def _get_indexable_versions():
        """Get all versions that need to be indexed by the catalog.
        """

class IVersion(Interface):
    """Version of a versioned object
    """

    def version_status():
        """Returns the current status of this version (unapproved, approved,
        public, last closed of closed)
        """

    def object_path():
        """Returns the physical path of the object this is a version of
        """

    def version():
        """Returns the version-id
        """

    def object():
        """Returns the object this is a version of
        """

    def publication_datetime():
        """Returns the version's publication datetime
        """

    def expiration_datetime():
        """Returns the version's expiration datetime
        """

    def get_version():
        """Returns itself. Used by acquisition to get the
           neared version.
        """

class INonPublishable(ISilvaObject):
    """An object that does not appear in the public view or table of
    contents directly.
    """
    pass

###############################################################
### Asset
###############################################################


class IAsset(INonPublishable):
    """An Asset.
    """

    # MANIPULATORS

    def update_quota():
        """Update used space, and verify quota for this asset.
        """

    def reset_quota():
        """Reset the status of the quota.
        """

    # ACCESSORS

    def get_filename():
        """Object's id is filename
        PUBLIC
        """
        pass

    def get_file_size():
        """Get the size of the file as it will be downloaded.
        PUBLIC
        """
        pass

    def get_mime_type():
        """Get the mime-type for this file.
        PUBLIC
        """
        pass


class IFile(IAsset):
    """A File object to encapsulate "downloadable" data
    """
    # MANIPULATORS

    def set_file_data(file):
        """Re-upload data for this file object. It will change the
        content_type, however id, _title, etc. will not change.
        """
        pass

    def set_text_file_data(datastr):
        """Set content of the file from the given string.
        """
        pass

    # ACCESSORS

    def tag(**kw):
        """Generate a tag to download file content.
        """
        pass

    def get_text_content():
        """Return the text content of the file or TypesError is it's
        not a text file.
        """
        pass

    def get_content():
        """Return the content of the file in any cases.
        """
        pass

    def get_content_fd():
        """Return a file descriptor to access the content of the file.
        """

    def get_download_url():
        """Obtain the public URL the public could use to download this
        file. Typically it's the URL used in ``tag``.
        """
        pass


class IZopeFile(IFile):
    """A file which is in fact a sub-file object.
    """

class IZODBFile(IZopeFile):
    """A file in ZODB.
    """

class IFileSystemFile(IZopeFile):
    """A file on the file system.
    """

class IBlobFile(IFile):
    """A file as a blob.
    """

class IImage(IAsset):
    """Images.
    """

    def set_image(file):
        """Set the image object.
        """

    def set_web_presentation_properties(web_format, web_scale, web_crop):
        """Sets format and scaling for web presentation.

        web_format (str): either JPEG or PNG (or whatever other format
        makes sense, must be recognised by PIL).
        web_scale (str): WidthXHeight or nn.n%.
        web_crop (str): X1xY1-X2xY2, crop-box or empty for no cropping.

        Raises ValueError if web_scale cannot be parsed.

        Automaticaly updates cached web presentation image.
        """

    def getOrientation():
        """Returns translated Image orientation (string).
        """

    def getDimensions(img=None):
        """Returns width, heigt of (hi res) image.

        Raises ValueError if there is no way of determining the dimenstions,
        Return 0, 0 if there is no image,
        Returns width, height otherwise.
        """

    def getFormat():
        """Returns image format.
        """

    def getImage(hires=1, webformat=0):
        """Return image data.
        """


###############################################################
### Ghost
###############################################################

class IGhost(Interface):
    """Interface for ghosts (and ghost folders)"""

    def haunted_path():
        """return path to haunted objecy"""

    def get_haunted_url():
        """return haunted object's url"""

    def get_haunted():
        """return the haunted object"""

    def _factory(container, id, content_url):
        """call factory method in container context"""

class IGhostContent(IGhost):
    """Marker interface for "normal" ghosts, i.e. Silva.Ghost.Ghost"""

class IGhostFolder(IGhost):
    """Marker interface for ghost folders"""


###############################################################
### Group
###############################################################

# XXX not really a content
class IBaseGroup(INonPublishable):
    """A group implementation.
    """

    def isValid():
        """Returns whether the group asset is valid.
        """

class IGroup(IBaseGroup):
    """Simple Group with user in it.
    """

class IIPGroup(IBaseGroup):
    """Group using IP as members.
    """

class IVirtualGroup(IBaseGroup):
    """Virtual group.
    """

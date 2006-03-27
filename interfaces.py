from zope.interface import Interface

from AccessControl import ModuleSecurityInfo
module_security = ModuleSecurityInfo('Products.Silva.interfaces')
__allow_access_to_unprotected_subobjects__ = 1

class IAccessManager(Interface):
    """Mixin class for objects to request local roles on the object"""

    def request_role(self, userid, role):
        """Request a role on the current object and send an e-mail to the
        editor/chiefeditor/manager"""

    def allow_role(self, userid, role):
        """Allows the role and send an e-mail to the user"""

    def deny_role(self, userid, role):
        """Denies the role and send an e-mail to the user"""

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

class ISilvaObject(ISecurity):
    """Interface that should be supported by all Silva objects.
    """
    # MANIPULATORS
    def set_title(title):
        """Change the title of the content object.
        """
        pass

    # MANIPULATORS
    def manage_afterAdd(item, container):
        """Hook called by Zope just after the item was added to
        container. Adds item id to an ordered list, if item is
        a publishable object.
        """
        pass

    def manage_beforeDelete(item, container):
        """Hook called by Zope just before the item is deleted from
        container. Removes item id to from ordered list (item is
        a publishable object).
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

    def is_cacheable():
        """Return true if the public view of this object can be safely cached.
        This means the public view should not contain any dynamically
        generated content.
        """

    def get_xml():
        """Render this object as XML, return as string in UTF-8 encoding.
        """
        pass

    def to_xml(f):
        """Render this object as XML, write unicode to fileobject f.
        """
        pass

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
    def activate():
        """Make this publishable item active.
        """
        pass

    def deactivate():
        """Deactivate publishable item.
        """
        pass

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

    def is_active():
        """Returns true if this object is actually active and
        in the table of contents.
        PUBLIC
        """
        pass

    def can_activate():
        pass

    def can_deactivate():
        pass


class IContainer(ISilvaObject, IPublishable):

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
        """Get a list of non-publishable objects in this folder.
        (not in any order).
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
    pass

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

    def can_approve():
        """Returns true if approval is allowed.
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

    def revert_to_previous():
        """The editable version will be replaced by a copy of the
        public version.
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

class RequiredParameterNotSetError(Exception):
    pass

class IAsset(ISilvaObject):
    """An object that does not appear in the publication's
    table of content directly.
    """

class IFile(IAsset):
    """A File object to encapsulate "downloadable" data
    """
    # MANIPULATORS

    def set_file_data(self, file):
        """Re-upload data for this file object. It will change the
        content_type, however id, _title, etc. will not change.
        """
        pass

    # ACCESSORS

    def get_filename(self):
        """Object's id is filename
        PUBLIC
        """
        pass

    def get_file_size(self):
        """Get the size of the file as it will be downloaded.
        PUBLIC
        """
        pass

    def get_mime_type(self):
        """Get the mime-type for this file.
        PUBLIC
        """
        pass

    def get_download_url(self):
        """Obtain the public URL the public could use to download this file
        PUBLIC
        """
        pass

    def get_download_link(
        self, title_attr='', name_attr='', class_attr='', style_attr=''):
        """Obtain a complete HTML hyperlink by which the public can download
        this file.
        PUBLIC
        """
        pass

# XXX just so we can register an adapter. SilvaFlashAsset should
# start using this
class IFlash(IFile):
    """Marker interface for flash assets.
    """
    pass

# XXX should be extended to non-marker status
class IImage(IAsset):
    """Marker interface for image assets.
    """
    
class IMember(Interface):
    # ACCESSORS
    def userid():
        """Return unique id for member/username
        """

    def fullname():
        """Return full name
        """

    def email():
        """Return users's email address if known, None otherwise.
        """

    def departments():
        """Return list of departments user is in, or None if no such information.
        """

    def extra(name):
        """Return bit of extra information, keyed by name.
        """

    def is_approved():
        """Return true if this member is approved. Unapproved members
        may face restrictions on the Silva site.
        """

class IMemberService(Interface):
    def extra():
        """Return list of names of extra information.
        """

    def find_members(search_string):
        """Return all users with a full name containing search string.
        """

    def is_user(userid):
        """Return true if userid is indeed a known user.
        """

    def get_member(userid):
        """Get member object for userid, or None if no such member object.
        """

    def get_cached_member(userid):
        """Get memberobject which can be cached, or None if no such memberobject.
        """

    def allow_authentication_requests():
        """Return true if authentication requests are allowed, false if not
        """

    def get_authentication_requests_url():
        """Returns the url of the authentication_requests form
        """

    def get_extra_names():
        """Return list of names of extra information.
        """

# there is also expected to be a 'Members' object that is traversable
# to a Member object. Users can then modify information in the member
# object (if they have the permissions to do so, but the user associated
# with the member should do so)

class IMessageService(Interface):

    def send_message(from_memberid, to_memberid, subject, message):
        """Send a message from one member to another.
        """

    def send_pending_messages():
        """Send all pending messages.

        This needs to be called at the end of a request otherwise any
        messages pending may be lost.
        """

class ISidebarService(Interface):
    def render(obj, tab_name):
        """Returns the rendered PT

        Checks whether the PT is already available cached, if so
        renders the tab_name into it and returns it, if not renders
        the full pagetemplate and stores that in the cache
        """

    def invalidate(obj):
        """Invalidate the cache for a specific object
        """


class IContainerPolicy(Interface):
    """Policy for container's default documents"""

    def createDefaultDocument(container, title):
        """create default document in given container"""


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


class IIcon(Interface):
    # XXX I don't like the name

    def getIconIdentifier():
        """returns icon identifier

            the icon registry should be able to return an icon from an icon
            identifier
        """

class IUpgrader(Interface):
    """interface for upgrade classes"""

    def upgrade(anObject):
        """upgrades object

            during upgrade the object identity of the upgraded object may
            change

            returns object
        """

class ISubscribable(Interface):
    """Subscribable interface
    """
    
    def isSubscribable():
        """Return True if the adapted object is actually subscribable,
        False otherwise.
        """
        pass
    
    def subscribability():
        """
        """
        pass
    
    def getSubscribedEmailaddresses():
        """
        """
        pass
    
    def getSubscriptions():
        """Return a list of ISubscription objects
        """
        pass
    
    def isValidSubscription(emailaddress, token):
        """Return True is the specified emailaddress and token depict a
        valid subscription request. False otherwise.
        """
        pass

    def isValidCancellation(emailaddress, token):
        """Return True is the specified emailaddress and token depict a
        valid cancellation request. False otherwise.
        """
        pass
    
    def isSubscribed(emailaddress):
        """Return True is the specified emailaddress is already subscribed
        for the adapted object. False otherwise.
        """
        pass    

    def setSubscribable(bool):
        """Set the subscribability to True or False for the adapted object.
        """
        pass
        
    def subscribe(emailaddress):
        """Subscribe emailaddress for adapted object.
        """
        pass
    
    def unsubscribe(emailaddress):
        """Unsubscribe emailaddress for adapted object.
        """
        pass

    def generateConfirmationToken(emailaddress):
        """Generate a token used for the subscription/cancellation cycle.
        """
        pass

class ISubscription(Interface):
    """Subscription interface
    """
    
    def emailaddress():
        """Return emailaddress for the subscription.
        """
        pass
        
    def contentSubscribedTo():
        """Return object for this subscription.
        """
        pass

class IHaunted(Interface):
    """Interface for haunted adapter
    """
    
    def getHaunting():
        """Return iterator of objects (ghosts) haunting the adapted object.
        """
        pass

class IAutoTOC(IContent):
    pass


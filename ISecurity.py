# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
import Interface

class ISecurity(Interface.Base):
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

    def sec_open_to_public():
        """Open this object to the public; accessible to everybody (if
        at least container is accessible).
        """

    def sec_close_to_public():
        """Close this object to the public; only accessible to people
        with Viewer role here.
        """

    def sec_create_lock():
        """Create lock for this object. Return true if successful.
        """
    
    # ACCESSORS

    def sec_is_open_to_public():
        """Check whether this is viewable by the public.
        """

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
    
    def sec_get_user_info(userid):
        """Get information for userid.
        FIXME: describe which info fields exist.
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

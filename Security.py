from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Security:
    """Can be mixed in with an object to support Silva security.
    (built on top of Zope security)
    Methods prefixed with sec_ so as not to disrupt similarly named
    Zope's security methods. (ugly..)
    """
    security = ClassSecurityInfo()
    
    # MANIPULATORS
    def sec_assign(self, userid, role):
        """Assign role to userid for this object.
        """
        self.manage_addLocalRoles(userid, [role])

    def sec_remove(self, userid):
        """Remove a user completely from this object.
        """
        self.manage_delLocalRoles([userid])

    def sec_revoke(self, userid, revoke_roles):
        """Remove roles from user in this object.
        """
        old_roles = self.get_local_roles_for_userid(userid)
        roles = [role for role in old_roles if role not in revoke_roles]
        self.manage_setLocalRoles(userid, roles)
    
    # ACCESSORS
    def sec_get_userids(self):
        """Get the userids that have local roles here.
        """
        return [userid for userid, roles in self.get_local_roles()]

    def sec_get_roles_for_userid(self, userid):
        """Get the local roles that a userid has here.
        """
        return self.get_local_roles_for_userid(userid)

    def sec_get_roles(self):
        """Get all roles defined here that we're interested in managing.
        """
        # FIXME: make this configurable?
        not_to_use_roles = ['Anonymous', 'Authenticated', 'Manager', 'Owner']
        return [role for role in self.valid_roles() if role not in not_to_use_roles]

    def sec_get_current_userids_on_clipboard(self):
        """Get list of users on the clipboard.
        """
        return []
    
    def sec_get_user_info(self, userid):
        """Get information for userid. FIXME: describe which info fields
        exist.
        """
        return {}

InitializeClass(Security)

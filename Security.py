from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
import SilvaPermissions

class Security:
    """Can be mixed in with an object to support Silva security.
    (built on top of Zope security)
    Methods prefixed with sec_ so as not to disrupt similarly named
    Zope's security methods. (ugly..)
    """
    security = ClassSecurityInfo()
    
    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'sec_assign')
    def sec_assign(self, userid, role):
        """Assign role to userid for this object.
        """
        self.manage_addLocalRoles(userid, [role])

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'sec_remove')
    def sec_remove(self, userid):
        """Remove a user completely from this object.
        """
        self.manage_delLocalRoles([userid])

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'sec_revoke')
    def sec_revoke(self, userid, revoke_roles):
        """Remove roles from user in this object.
        """
        old_roles = self.get_local_roles_for_userid(userid)
        roles = [role for role in old_roles if role not in revoke_roles]
        if len(roles) > 0:
            self.manage_setLocalRoles(userid, roles)
        else:
            # if no more roles, remove user completely
            self.sec_remove(userid)
            
    # ACCESSORS
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'sec_get_user_ids')
    def sec_get_userids(self):
        """Get the userids that have local roles here that we care about.
        """
        interesting_roles = self.sec_get_roles()
        result = []
        for userid, roles in self.get_local_roles():
            for role in roles:
                if role in interesting_roles:
                    result.append(userid)
                    break
        return result

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'sec_get_roles_for_userid')
    def sec_get_roles_for_userid(self, userid):
        """Get the local roles that a userid has here.
        """
        return self.get_local_roles_for_userid(userid)

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'sec_get_roles')
    def sec_get_roles(self):
        """Get all roles defined here that we can manage, given the
        roles of this user.
        """
        # FIXME: make this configurable?
        not_to_use_roles = ['Anonymous', 'Authenticated', 'Manager', 'Owner']
        return [role for role in self.valid_roles() if role not in not_to_use_roles]


    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'sec_get_current_userids_on_clipboard')  
    def sec_get_current_userids_on_clipboard(self):
        """Get list of users on the clipboard.
        """
        return ['foo', 'bar']

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_get_user_info')  
    def sec_get_user_info(self, userid):
        """Get information for userid. FIXME: describe which info fields
        exist.
        """
        return {}

InitializeClass(Security)

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
import SilvaPermissions
from UserManagement import user_management
import Interfaces

interesting_roles = ['Author', 'Editor', 'ChiefEditor', 'Manager']

def are_we_manager(user):
    f.REQUEST.AUTHENTICATED_USER.has_roles(['Manager'], self)
class Security:
    """Can be mixed in with an object to support Silva security.
    (built on top of Zope security)
    Methods prefixed with sec_ so as not to disrupt similarly named
    Zope's security methods. (ugly..)
    """
    security = ClassSecurityInfo()

    _last_author_userid = None
    _last_author_info = None
    
    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_assign')
    def sec_assign(self, userid, role):
        """Assign role to userid for this object.
        """
        if role not in interesting_roles:
            return
        # check whether we have permission to add Manager
        if (role == 'Manager' and
            not self.sec_have_management_rights()):
            return
        self.manage_addLocalRoles(userid, [role])

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_remove')
    def sec_remove(self, userid):
        """Remove a user completely from this object.
        """
        # FIXME: should this check for non Silva roles and keep
        # user if they exist?
        # can't remove managers if we don't have the rights to do so
        if ('Manager' in self.sec_get_roles_for_userid(userid) and
            not self.sec_have_management_rights()):
            return
        self.manage_delLocalRoles([userid])

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_revoke')
    def sec_revoke(self, userid, revoke_roles):
        """Remove roles from user in this object.
        """
        for role in revoke_roles:
            if role not in interesting_roles:
                return
            # can't revoke manager roles if we're not manager
            if (role == 'Manager' and
                not self.sec_have_management_rights()):
                return
        old_roles = self.get_local_roles_for_userid(userid)
        roles = [role for role in old_roles if role not in revoke_roles]
        if len(roles) > 0:
            self.manage_setLocalRoles(userid, roles)
        else:
            # if no more roles, remove user completely
            self.sec_remove(userid)
            
    # ACCESSORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_have_management_rights')
    def sec_have_management_rights(self):
        """Check whether we have management rights here.
        """
        return self.REQUEST.AUTHENTICATED_USER.has_role(['Manager'], self)
    
    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_get_user_ids')
    def sec_get_userids(self):
        """Get the userids that have local roles here that we care about.
        """
        result = []
        for userid, roles in self.get_local_roles():
            for role in roles:
                if role in interesting_roles:
                    result.append(userid)
                    break
        return result

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_get_roles_for_userid')
    def sec_get_roles_for_userid(self, userid):
        """Get the local roles that a userid has here.
        """
        return [role for role in self.get_local_roles_for_userid(userid)
                if role in interesting_roles]
    
    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_get_roles')
    def sec_get_roles(self):
        """Get all roles defined here that we can manage, given the
        roles of this user.
        """
        return interesting_roles

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_find_users')
    def sec_find_users(self, userid):
        """Find users in user database.
        """
        return user_management.find_users(self, userid)
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_get_user_info')  
    def sec_get_user_info(self, userid):
        """Get information for userid. FIXME: describe which info fields
        exist.
        """
        return user_management.get_user_info(self, userid)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_get_last_author_info')
    def sec_get_last_author_info(self):
        """Get the info of the last author (provide at least cn and
        userid).
        """
        # containers have no author
        if Interfaces.Container.isImplementedBy(self):
            return { 'cn': '', 'userid': None }

        # unknown author if none assigned yet
        if not self._last_author_userid:
            return { 'cn': 'Unknown author', 'userid': None }
        # authorwise get cached author info
        return self._last_author_info

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_set_last_author_info')
    def sec_update_last_author_info(self):
        """Update the author info with the current author.
        """
        self._last_author_userid = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self._last_author_info = self.sec_get_user_info(self._last_author_userid)
        
InitializeClass(Security)

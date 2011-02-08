# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base
from App.class_init import InitializeClass
from DateTime import DateTime

from zope.component import getUtility

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva import roleinfo
from Products.Silva.Membership import noneMember

from silva.core.interfaces import IVersion, IRoot
from silva.core.services.interfaces import IMemberService

from Products.SilvaMetadata.interfaces import IMetadataService


class SecurityError(Exception):
    """An error has been triggered by the security system.
    """

class UnauthorizedRoleAssignement(SecurityError):
    """This roles can be assigned.
    """

class Security(object):
    """Can be mixed in with an object to support Silva security.
    (built on top of Zope security)
    Methods prefixed with sec_ so as not to disrupt similarly named
    Zope's security methods. (ugly..)
    """
    security = ClassSecurityInfo()

    _last_author_userid = None
    _last_author_info = None

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_get_userids')
    def sec_get_userids(self):
        """Get the userids that have local roles here that we care about.
        """
        result = []
        for userid, roles in self.get_local_roles():
            for role in roles:
                if role in roleinfo.ASSIGNABLE_ROLES:
                    result.append(userid)
                    break
        return result

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'sec_get_nearest_of_role')
    def sec_get_nearest_of_role(self, role):
        """Get a list of userids that have a role in this context. This
        goes up the tree and finds the nearest user(s) that can be found.
        """
        obj = self.aq_inner
        while 1:
            # get all users defined on this object
            userids = obj.sec_get_userids()
            if userids:
                result = []
                for userid in userids:
                    if (role in obj.sec_get_roles_for_userid(userid) and
                            self.service_members.get_member(userid)):
                        result.append(userid)
                if result:
                    return result

            if IRoot.providedBy(obj):
                break
            obj = obj.aq_parent
        return []

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'sec_get_roles_for_userid')
    def sec_get_roles_for_userid(self, userid):
        """Get the local roles that a userid has here.
        """
        return [role for role in self.get_local_roles_for_userid(userid)
                if role in roleinfo.ASSIGNABLE_ROLES]

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'sec_get_last_author_info')
    def sec_get_last_author_info(self, version=None):
        """Get the info of the last author of the
           passed in version (this is a IMember object)
           if version is none, get the info for the
           previewable version.
        """
        #the version parameter was added to support
        # getting the last author info for the correct
        # version in the silva-extra metadata
        # (this was always returning the previewable
        # version's info, even if the version in question
        # was the published or closed version

        # get cached author info (may be None)
        if not version:
            version = self.get_previewable()
        if not (version or IVersion.providedBy(self)):
            return noneMember.__of__(self)

        info = getattr(version, '_last_author_info', None)
        if info is None:
            return noneMember.__of__(self)
        else:
            return info.__of__(self)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_update_last_author_info')
    def sec_update_last_author_info(self):
        """Update the author info with the current author.
        """
        version = self.get_editable()
        if version is not None:
            user_id = getSecurityManager().getUser().getId()
            member = getUtility(IMemberService)
            user = member.get_cached_member(user_id, location=self)
            version._last_author_userid = user_id
            version._last_author_info = aq_base(user)
            binding = getUtility(IMetadataService).getMetadata(version)
            if binding is None:
                return
            now = DateTime()
            binding.setValues('silva-extra', {'modificationtime': now})

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'sec_get_creator_info')
    def sec_get_creator_info(self):
        service = getUtility(IMemberService)
        user_id = self.getOwner().getId()
        if not user_id:
            return noneMember.__of__(self)
        return service.get_cached_member(user_id, location=self)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'sec_get_all_roles')
    def sec_get_all_roles(self, userid=None):
        """Returns all roles the user has in this context.  If userid
        is None, then return all roles for the currently logged in
        user
        """
        roles = []
        if not userid:
            user = getSecurityManager().getUser()
        else:
            user = self.acl_users.getUser(userid)
        for role in roleinfo.ASSIGNABLE_ROLES[:]:
            if user.has_role(role, self):
                roles.append(role)
        return roles


InitializeClass(Security)

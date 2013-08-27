# -*- coding: utf-8 -*-
# Copyright (c) 2003-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import urllib
import hashlib

from five import grok

# zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# silva
from Products.Silva import SilvaPermissions
from Products.Silva import roleinfo
from Products.Silva.icon import Icon
from Products.Silva.Membership import cloneMember, Member
from Products.Silva.Security import Security
from Products.Silva.helpers import add_and_edit

from silva.core.services.interfaces import IMemberService, MemberLookupError
from silva.core.services.base import SilvaService, ZMIObject
from silva.core import interfaces
from silva.core import conf as silvaconf
from silva.translations import translate as _

# This is not yet in use.
GRAVATAR_URL = "https://secure.gravatar.com/avatar/"

class GravatarIcon(Icon):

    def __init__(self, icon):
        self.icon = icon

    def url(self, resolver, content):
        if content is not None:
            if interfaces.IAuthorization.providedBy(content):
                content = content.source
            email = content.avatar()
            if email:
                return (GRAVATAR_URL +
                        hashlib.md5(email.lower()).hexdigest() +
                        urllib.urlencode({'default': 'default', 'size': 16}))
        return super(GravatarIcon, self).url(resolver, content)


class SimpleMember(Member, Security, ZMIObject):
    """Silva Simple Member"""

    grok.implements(interfaces.IEditableMember)
    security = ClassSecurityInfo()

    meta_type = 'Silva Simple Member'

    silvaconf.icon('icons/member.png')
    silvaconf.factory('manage_addSimpleMemberForm')
    silvaconf.factory('manage_addSimpleMember')

    # BBB
    _avatar = None

    def __init__(self, id):
        self.id = id
        self._title = id
        self._fullname = None
        self._email = None
        self._avatar = None
        self._creation_datetime = self._modification_datetime = DateTime()
        self._is_approved = 0

    security.declarePrivate('allowed_roles')
    def allowed_roles(self):
        return roleinfo.ASSIGNABLE_ROLES

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_fullname')
    def set_fullname(self, fullname):
        """set the full name"""
        self._fullname = fullname

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_email')
    def set_email(self, email):
        """ set the email address.
           (does not test, if email address is valid)
        """
        self._email = email

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_avatar')
    def set_avatar(self, avatar):
        """Set the email address to be used by gravatar"""
        self._avatar = avatar

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'approve')
    def approve(self):
        """Approve the member"""
        self._is_approved = 1

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'userid')
    def userid(self):
        """userid
        """
        return self.id

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fullname')
    def fullname(self):
        """fullname
        """
        if self._fullname is None:
            return self.id
        return self._fullname

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'email')
    def email(self):
        """email
        """
        return self._email

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'extra')
    def extra(self, name):
        """Return bit of extra information, keyed by name.
        """
        #For CachedMember accessing of the avatar tag
        #Should be 'avatar_tag:SIZE' -- ie, 'avatar_tag:32'
        if name.startswith("avatar_tag"):
            return self.avatar_tag(name.split(':')[1])

        return None

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'avatar')
    def avatar(self):
        """Return the email address to be used by gravatar. Return '' if
        no address has been specified.
        """
        return self._avatar if self._avatar is not None else self._email


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_approved')
    def is_approved(self):
        """is_approved
        """
        return self._is_approved


InitializeClass(SimpleMember)

manage_addSimpleMemberForm = PageTemplateFile(
    "www/simpleMemberAdd", globals(),
    __name__='manage_addSimpleMemberForm')

def manage_addSimpleMember(self, id, REQUEST=None):
    """Add a Simple Member."""
    user = SimpleMember(id)
    self._setObject(id, user)
    user = self._getOb(id)
    user.manage_addLocalRoles(id, ['ChiefEditor'])
    add_and_edit(self, id, REQUEST)
    return ''


class SimpleMemberService(SilvaService):
    grok.implements(IMemberService)
    grok.baseclass()
    silvaconf.icon('icons/service_member.png')
    security = ClassSecurityInfo()
    meta_type = 'Silva Simple Member Service'

    # XXX will be used by access tab and should be opened wider if this
    # is central service..
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'find_members')
    def find_members(self, search_string, location=None):
        if len(search_string) < 2:
            raise MemberLookupError(
                _(u"The search input is too short. "
                  u"Please enter two or more characters."))
        # XXX: get_valid_userids is evil: will break with other user
        # folder implementations.
        userids = self.get_valid_userids()
        result = []
        for userid in userids:
            if userid.find(search_string) != -1:
                result.append(self.get_cached_member(userid))
        return result

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_user')
    def is_user(self, userid, location=None):
        # XXX: get_valid_userids is evil: will break with other user
        # folder implementations.
        if location is None:
            location = self
        return userid in location.get_valid_userids()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_member')
    def get_member(self, userid, location=None):
        if not self.is_user(userid, location=location):
            return None
        # get member, add it if it doesn't exist yet
        members = self.get_root()._getOb('Members')
        member = members._getOb(userid, None)
        if member is None:
            members.manage_addProduct['Silva'].manage_addSimpleMember(userid)
            member = members._getOb(userid)
        return member

    def get_display_usernames(self):
        return False

    def get_display_emails(self):
        return False

    def get_redirect_to_root(self):
        return False

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_cached_member')
    def get_cached_member(self, userid, location=None):
        """Returns a cloned member object, which can be stored in the ZODB"""
        return cloneMember(self.get_member(userid, location=location)).__of__(self)

    security.declarePublic('logout')
    def logout(self, came_from=None, REQUEST=None):
        """Logout the user.
        """
        if REQUEST is None and hasattr(self, REQUEST):
            REQUEST = self.REQUEST
        if REQUEST is None:
            return
        # URL2 removes service_members/logout
        REQUEST.RESPONSE.redirect(REQUEST.URL2 + '/edit/logout')


InitializeClass(SimpleMemberService)


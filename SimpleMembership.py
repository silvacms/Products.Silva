# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import urllib
import hashlib

from five import grok
from zope import interface, schema

# zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# silva
from Products.Silva import SilvaPermissions
from Products.Silva import roleinfo
from Products.Silva.Membership import cloneMember, Member
from Products.Silva.Security import Security
from Products.Silva.helpers import add_and_edit

from silva.core.services.interfaces import IMemberService
from silva.core.services.base import SilvaService, ZMIObject
from silva.core import interfaces
from silva.core import conf as silvaconf
from silva.translations import translate as _
from zeam.form import silva as silvaforms


GRAVATAR_URL = "https://secure.gravatar.com/avatar.php?"
GRAVATAR_TEMPLATE = """
<img src="%(image)s" alt="%(userid)s's avatar" title="%(userid)s's avatar"
     style="height: %(size)spx; width: %(size)spx" />
"""


class SimpleMember(Member, Security, ZMIObject):
    """Silva Simple Member"""

    grok.implements(interfaces.IEditableMember)

    security = ClassSecurityInfo()

    meta_type = 'Silva Simple Member'

    silvaconf.icon('www/member.png')
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

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'security_trigger')
    def security_trigger(self):
        pass

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
                              'avatar_tag')
    def avatar_tag(self, size=32):
        """HTML <img /> tag for the avatar icon
        """
        #See http://en.gravatar.com/site/implement/python
        email = self.avatar()
        default = self.get_root_url() + "/globals/avatar.png"

        if email:
            url = GRAVATAR_URL + urllib.urlencode(
                {'gravatar_id':hashlib.md5(email.lower()).hexdigest(),
                 'default':default, 'size':str(size)})
        else:
            url = default
        info = {'userid': self.userid(),
                'size': size,
                'image': url}
        return GRAVATAR_TEMPLATE % info

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
    user = getattr(self, id)
    user.manage_addLocalRoles(id, ['ChiefEditor'])
    add_and_edit(self, id, REQUEST)
    return ''


class SimpleMemberService(SilvaService):
    meta_type = 'Silva Simple Member Service'
    title = 'Silva Membership Service'
    default_service_identifier = 'service_members'
    _use_direct_lookup = False
    _allow_authentication_requests = False

    grok.implements(IMemberService)
    silvaconf.icon('www/members.png')
    security = ClassSecurityInfo()

    manage_options = (
        {'label':'Configure', 'action':'manage_configure'},
        ) + SilvaService.manage_options


    # XXX will be used by access tab and should be opened wider if this
    # is central service..
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'find_members')
    def find_members(self, search_string, location=None):
        # XXX: get_valid_userids is evil: will break with other user
        # folder implementations.
        userids = self.get_valid_userids()
        result = []
        for userid in userids:
            if userid.find(search_string) != -1:
                result.append(self.get_cached_member(userid))
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_user')
    def is_user(self, userid, location=None):
        # XXX: get_valid_userids is evil: will break with other user
        # folder implementations.
        if location is None:
            location = self
        return userid in location.get_valid_userids()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_member')
    def get_member(self, userid, location=None):
        if not self.is_user(userid, location=None):
            return None
        # get member, add it if it doesn't exist yet
        members = self.Members.aq_inner.aq_explicit
        member = getattr(members, userid, None)
        if member is None:
            members.manage_addProduct['Silva'].manage_addSimpleMember(userid)
            member = getattr(members, userid)
        return member

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_cached_member')
    def get_cached_member(self, userid, location=None):
        """Returns a cloned member object, which can be stored in the ZODB"""
        return cloneMember(self.get_member(userid, location=location)).__of__(self)

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_use_direct_lookup')
    def set_use_direct_lookup(self, value):
        """sets use_direct_lookup"""
        self._use_direct_lookup = value

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'use_direct_lookup')
    def use_direct_lookup(self):
        return self._use_direct_lookup

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'allow_authentication_requests')
    def allow_authentication_requests(self):
        return self._allow_authentication_requests

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_allow_authentication_requests')
    def set_allow_authentication_requests(self, value):
        """sets allow_authentication_requests"""
        self._allow_authentication_requests = value

    security.declareProtected('View management screens',
                              'manage_allowAuthenticationRequests')
    def manage_allowAuthenticationRequests(self, REQUEST):
        """manage method to set allow_authentication_requests"""
        self.set_allow_authentication_requests(int(REQUEST['allow_authentication_requests']))
        return self.manage_editForm(manage_tabs_message='Changed settings')

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_authentication_requests_url')
    def get_authentication_requests_url(self):
        """Return the url for the authentication_requests form, relative from resources
        directory (so including the escaped productname!!)
        """
        return None

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



class IServiceSetting(interface.Interface):
    _use_direct_lookup = schema.Bool(
        title=_(u"Use direct lookup?"),
        description=_(u"Disable search feature to affect a role to a user."))
    _allow_authentication_requests = schema.Bool(
        title=_(u"Allow membership requests on this site ?"),
        description=_(u"Proprose to users to request for roles on content."))


class EditMemberService(silvaforms.ZMIForm):
    grok.context(SimpleMemberService)
    grok.name('manage_configure')

    label = _(u"Configure member service")
    description = _(u"Update member service settings.")
    ignoreContent = False
    fields = silvaforms.Fields(IServiceSetting)
    actions = silvaforms.Actions(silvaforms.EditAction(_(u"Update")))

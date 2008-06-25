from zope.interface import implements

# zope
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Globals
from DateTime import DateTime

# silva
from Security import Security
from Membership import cloneMember, Member
import SilvaPermissions
from helpers import add_and_edit

from interfaces import IMember, IMemberService

class SimpleMember(Member, Security, SimpleItem.SimpleItem):
    """Silva Simple Member"""

    implements(IMember)

    security = ClassSecurityInfo()

    meta_type = 'Silva Simple Member'
    
    def __init__(self, id):
        self.id = id
        self._title = id
        self._fullname = None
        self._email = None
        self._creation_datetime = self._modification_datetime = DateTime()
        self._is_approved = 0

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'security_trigger')
    def security_trigger(self):
        pass

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_fullname')
    def set_fullname(self, fullname):
        """set the full name"""
        self._fullname = fullname
        self._p_changed = 1

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_email')
    def set_email(self, email):
        """ set the email address.
           (does not test, if email address is valid)
        """
        self._email = email
        self._p_changed = 1

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_editor')
    def set_editor(self, editor):
        """Set the user's preferred editor"""
        self._editor = editor

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'approve')
    def approve(self):
        """Approve the member"""
        self._is_approved = 1
        self._p_changed = 1
    
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
                              'is_approved')
    def is_approved(self):
        """is_approved
        """
        return self._is_approved

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'extra') 
    def extra(self, name):
        """Not implemented for simple membership.
        """
        pass
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'editor')
    def editor(self):
        """Return the id of the member's favorite editor"""
        return getattr(self, '_editor', self.default_editor())

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'default_editor')
    def default_editor(self):
        """Return the id of the default editor"""
        if hasattr(self, 'service_kupu'):
            return 'kupu'
        else:
            return 'field editor'


Globals.InitializeClass(SimpleMember)

manage_addSimpleMemberForm = PageTemplateFile(
    "www/simpleMemberAdd", globals(),
    __name__='manage_addSimpleMemberForm')

def manage_addSimpleMember(self, id, REQUEST=None):
    """Add a Simple Member."""
    object = SimpleMember(id)
    self._setObject(id, object)
    object.sec_assign(id, 'ChiefEditor')
    add_and_edit(self, id, REQUEST)
    return ''

class SimpleMemberService(SimpleItem.SimpleItem):
    implements(IMemberService)

    security = ClassSecurityInfo()

    meta_type = 'Silva Simple Member Service'
    title = 'Silva Membership Service'
    
    manage_options = (
        {'label':'Edit', 'action':'manage_editForm'},
        ) + SimpleItem.SimpleItem.manage_options

    security.declareProtected('View management screens', 'manage_editForm')
    manage_editForm = PageTemplateFile(
        'www/simpleMemberServiceEdit', globals(),  __name__='manage_editForm')

    security.declareProtected('View management screens', 'manage_main')
    manage_main = manage_editForm

    def __init__(self, id):
        self.id = id
        self._allow_authentication_requests = 0

    # XXX will be used by access tab and should be opened wider if this
    # is central service..
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'find_members')
    def find_members(self, search_string):
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
    def is_user(self, userid):
        # XXX: get_valid_userids is evil: will break with other user
        # folder implementations.
        return userid in self.get_valid_userids()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_member')
    def get_member(self, userid):
        if not self.is_user(userid):
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
    def get_cached_member(self, userid):
        """Returns a cloned member object, which can be stored in the ZODB"""
        return cloneMember(self.get_member(userid)).__of__(self)

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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_extra_names')
    def get_extra_names(self):
        return []
    
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


Globals.InitializeClass(SimpleMemberService)

manage_addSimpleMemberServiceForm = PageTemplateFile(
    "www/simpleMemberServiceAdd", globals(),
    __name__='manage_addSimpleMemberServiceForm')

def manage_addSimpleMemberService(self, id, REQUEST=None):
    """Add a Simple Member Service."""
    object = SimpleMemberService(id)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''


from IMembership import IMember, IMemberService
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Membership import cloneMember
import Globals
import SilvaPermissions
from helpers import add_and_edit

class SimpleMember(SimpleItem.SimpleItem):
    __implements__ = IMember

    security = ClassSecurityInfo()

    meta_type = 'Silva Simple Member'
    
    def __init__(self, id):
        self.id = id
        self._fullname = None
        self._email = None
        self._departments = None
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_fullname')
    def set_fullname(self, fullname):
        self._fullname = fullname

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_email')
    def set_email(self, email):
        self._email = email

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_departments')
    def set_departments(self, departments):
        self._departments = departments
        
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
                              'departments')
    def departments(self):
        """departments
        """
        return self._departments
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_approved')
    def is_approved(self):
        """is_approved
        """
        return 1
    
Globals.InitializeClass(SimpleMember)

manage_addSimpleMemberForm = PageTemplateFile(
    "www/simpleMemberAdd", globals(),
    __name__='manage_addSimpleMemberForm')

def manage_addSimpleMember(self, id, REQUEST=None):
    """Add a Simple Member."""
    object = SimpleMember(id)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''

class SimpleMemberService(SimpleItem.SimpleItem):
    __implements__ = IMemberService

    security = ClassSecurityInfo()

    meta_type = 'Silva Simple Member Service'
    
    def __init__(self, id):
        self.id = id
        
    # XXX will be used by access tab and should be opened wider if this
    # is central service..
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'find_members')
    def find_members(self, search_string):
        userids = self.get_valid_userids()
        result = []
        for userid in userids:
            if userid.find(search_string) != -1:
                result.append(self.get_member(userid))
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_user')
    def is_user(self, userid):
        return userid in self.get_valid_userids()
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_member')
    def get_member(self, userid):
        if not self.is_user(userid):
            return None
        # get member, add it if it doesn't exist yet
        members = self.Members.aq_inner
        member = getattr(members, userid, None)
        if member is None:
            members.manage_addProduct['Silva'].manage_addSimpleMember(userid)
            member = getattr(members, userid)
        return cloneMember(member).__of__(self)

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

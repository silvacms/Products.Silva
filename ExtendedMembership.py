import smtplib
from DateTime import DateTime
from OFS import SimpleItem
from IMembership import IMember, IMemberService
from SimpleMembership import SimpleMember, SimpleMemberService
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Content import Content
import Globals
import SilvaPermissions
from Membership import cloneMember, noneMember
from helpers import add_and_edit

class ExtendedMember(Content, SimpleMember):
    """Extended member"""

    __implements__ = IMember

    security = ClassSecurityInfo()

    meta_type = 'Silva Extended Member'

    def __init__(self, id):
        self.id = id
        self._fullname = None
        self._email = None
        self._departments = None
        self._title = id
        self._creation_datetime = self._modification_datetime = DateTime()
        self._address = None
        self._postal_code = None
        self._city = None
        self._country = None
        self._telephone = None
        self._fax = None
        self._approved = 0

    # override manage_afterAdd and manage_beforeDelete from SilvaObject, since
    #   they expect the parent folder to be a Silva folder as well
    def manage_afterAdd(self, item, container):
        # make the user the current object reflects chief-editor on the object as well, so he can edit his data
        self.sec_assign(self.id, 'ChiefEditor')

    def manage_beforeDelete(self, item, container):
        pass

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'security_trigger')
    def security_trigger(self):
        pass

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_address')
    def set_address(self, address):
        """set address"""
        self._address = address

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_postal_code')
    def set_postal_code(self, pc):
        """set postal code"""
        self._postal_code = pc

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_city')
    def set_city(self, city):
        """set city"""
        self._city = city

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_country')
    def set_country(self, country):
        """set country"""
        self._country = country

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_telephone')
    def set_telephone(self, telephone):
        """set telephone number"""
        self._telephone = telephone

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_fax')
    def set_fax(self, fax):
        """set fax"""
        self._fax = fax

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'approve')
    def approve(self):
        """approve member"""
        self._approved = 1
        self._p_changed = 1

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'address')
    def address(self):
        """returns address"""
        return self._address

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'postal_code')
    def postal_code(self):
        """return postal code"""
        return self._postal_code

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'city')
    def city(self):
        """returns the city"""
        return self._city

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'country')
    def country(self):
        """returns the country"""
        return self._country

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'telephone')
    def telephone(self):
        """returns the telephone number"""
        return self._telephone

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fax')
    def fax(self):
        """returns the fax number"""
        return self._fax

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_approved')
    def is_approved(self):
        """is_approved
        """
        return self._approved

Globals.InitializeClass(ExtendedMember)

manage_addExtendedMemberForm = PageTemplateFile(
    "www/extendedMemberAdd", globals(),
    __name__='manage_addExtendedMemberForm')

def manage_addExtendedMember(self, id, REQUEST=None):
    """Add a Extended Member."""
    object = ExtendedMember(id)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''

class ExtendedMemberService(SimpleMemberService):
    __implements__ = IMemberService

    security = ClassSecurityInfo()

    meta_type = 'Silva Extended Member Service'

    manage_options = (
        {'label':'Edit', 'action':'manage_editForm'},
        ) + SimpleItem.SimpleItem.manage_options

    security.declareProtected('View management screens', 'manage_editForm')
    manage_editForm = PageTemplateFile(
        'www/extendedMemberServiceEdit', globals(),  __name__='manage_editForm')

    security.declareProtected('View management screens', 'manage_main')
    manage_main = manage_editForm

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'add_member')
    def add_member(self, member):
        """adds a member object to the member service"""
        if not member.userid in self.get_valid_userids():
            userfolder = self.acl_users.aq_inner
            userfolder.userFolderAddUser(member.userid)
        members = self.Members.aq_inner
        if hasattr(members, member.userid):
            raise Exception, 'Member already exists!'
        setattr(members, member.userid, member)
        # does this work for other objects besides self as well?
        members._p_changed = 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_member_object')
    def get_member_object(self, userid):
        """Returns the memberobject"""
        if not self.is_user(userid):
            return None
        # get member, add it if it doesn't exist yet
        members = self.Members.aq_inner
        member = getattr(members, userid, None)
        if member is None:
            members.manage_addProduct['Silva'].manage_addExtendedMember(userid)
            member = getattr(members, userid)
        return member

    # the following method is copied from the superclass only because the object to be created
    #   (if a member doesn't exist yet) should be an ExtendedMember instead of a SimpleMember
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_member')
    def get_member(self, userid):
        """Return clone of memberobject containing the main data fields.

        Can be used to store in the ZODB"""
        return cloneMember(self.get_member_object(userid)).__of__(self)

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'approve_member')
    def approve_member(self, userid):
        """Approve a member"""
        member = self.get_member_object(userid)
        member.approve_member()
        # send an e-mail?

    security.declarePublic('allow_subscription')
    def allow_subscription(self):
        """returns true if the service allows users to subscribe as a visitor or member"""
        return hasattr(self, '_allow_subscription') and self._allow_subscription

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_allow_subscription')
    def set_allow_subscription(self, value):
        """sets allow_subscription"""
        self._allow_subscription = value

    security.declareProtected('View management screens',
                              'manage_allowSubscription')
    def manage_allowSubscription(self, REQUEST):
        """manage method to set allow_subscription"""
        self.set_allow_subscription(int(REQUEST['allow_subscription']))

Globals.InitializeClass(ExtendedMemberService)

manage_addExtendedMemberServiceForm = PageTemplateFile(
    "www/extendedMemberServiceAdd", globals(),
    __name__='manage_addExtendedMemberServiceForm')

def manage_addExtendedMemberService(self, id, REQUEST=None):
    """Add a Extended Member Service."""
    object = ExtendedMemberService(id)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''


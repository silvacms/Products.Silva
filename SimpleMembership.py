import smtplib
from IMembership import IMember, IMemberService, IMemberMessageService
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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'allow_subscription')
    def allow_subscription(self):
        return 0

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

class EmailMessageService(SimpleItem.SimpleItem):
    """Simple implementation of IMemberMessageService that sends email
    messages.
    """
    
    meta_type = 'Silva Email Message Service'

    security = ClassSecurityInfo()

    __implements__ = IMemberMessageService

    manage_options = (
        {'label':'Edit', 'action':'manage_editForm'},
        ) + SimpleItem.SimpleItem.manage_options

    security.declareProtected('View management screens', 'manage_editForm')
    manage_editForm = PageTemplateFile(
        'www/emailMessageServiceEdit', globals(),  __name__='manage_editForm')

    security.declareProtected('View management screens', 'manage_main')
    manage_main = manage_editForm

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._host = None
        self._port = 25
        self._fromaddr = None

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_server')
    def set_server(self, host, port=25):
        self._host = host
        self._port = port

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'set_from_address')
    def set_from_address(self, fromaddr):
        self._fromaddr = fromaddr

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'server')
    def server(self):
        """Returns (host, port)"""
        return (self._host, self._port)

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'host')
    def host(self):
        """return self._host"""
        return self._host

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'port')
    def port(self):
        """return self._port"""
        return self._port

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'fromaddr')
    def fromaddr(self):
        """return self._fromaddr"""
        return self._fromaddr

    # XXX these security settings are not the right thing.. perhaps
    # create a new permission?
    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'send_message')
    def send_message(self, from_memberid, to_memberid, subject, message):
        if not hasattr(self.aq_base, '_v_messages'):
            self._v_messages = {}
        self._v_messages.setdefault(to_memberid, {}).setdefault(from_memberid, []).append((subject, message))

    # XXX have to open this up to the world, unfortunately..
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'send_pending_messages')
    def send_pending_messages(self):
        if not hasattr(self.aq_base, '_v_messages'):
            self._v_messages = {}
        for to_memberid, message_dict in self._v_messages.items():
            to_email = self.service_members.get_member(to_memberid).email()
            if to_email is None:
                print "messages: no email for: %s" % to_memberid
                to_email = to_memberid + "@madeup.infrae.com"
                # no email address known, so can't send these messages!
                #continue
            lines = []
            for from_memberid, messages in message_dict.items():
                print "From memberid:", from_memberid
                from_email = self.service_members.get_member(from_memberid).email()
                # XXX what if no from_email?
                lines.append("Message from: %s %s" %
                             (from_memberid, from_email))
                for subject, message in messages:
                    lines.append(subject)
                    lines.append('')
                    lines.append(message)
                    lines.append('')
            text = '\n'.join(lines)
            self._send_email(to_email, text)
        self._v_messages = {}

    def _send_email(self, toaddr, msg):
        msg = 'From: %s\r\nTo: %s\r\n\r\n%s' % (self._fromaddr, toaddr, msg)
        print "messages:"
        print msg
        server = smtplib.SMTP(self._host, self._port)
        server.sendmail(self._fromaddr, [toaddr], msg)
        server.quit()

    def manage_editEmailMessageService(self, REQUEST):
        """manage method to update data"""
        if not REQUEST['host'] or not REQUEST['port'] or not REQUEST['fromaddr']:
            return self.manage_main(manage_tabs_message='All fields are required!')
        self.set_server(REQUEST['host'], int(REQUEST['port']))
        self.set_from_address(REQUEST['fromaddr'])
        return self.manage_main()

Globals.InitializeClass(EmailMessageService)

manage_addEmailMessageServiceForm = PageTemplateFile(
    "www/serviceEmailMessageServiceAdd", globals(), __name__='manage_addEmailMessageServiceForm')

def manage_addEmailMessageService(self, id, title='', REQUEST=None):
    """Add member message service."""
    object = EmailMessageService(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''

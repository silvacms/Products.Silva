# some common classes used by Membership implementations
from AccessControl import ClassSecurityInfo
import Globals
from IMembership import IMember
from Globals import Persistent
import SilvaPermissions
import Acquisition

class Member(Persistent, Acquisition.Implicit):
    __implements__ = IMember
    security = ClassSecurityInfo()
    
    def __init__(self, userid, fullname, email, is_approved):
        self.id = userid
        self._fullname = fullname
        self._email = email
        self._approved = is_approved
        
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
        """Is approved
        """
        return self._approved

Globals.InitializeClass(Member)

class NoneMember(Persistent, Acquisition.Implicit):
    __implements__ = IMember

    security = ClassSecurityInfo()
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'userid')
    def userid(self):
        """userid
        """
        return 'unknown'

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fullname')
    def fullname(self):
        """fullname
        """
        return 'Unknown User'
        
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'email')
    def email(self):
        """email
        """
        return None
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_approved')
    def is_approved(self):
        """Is approved
        """
        return 0

Globals.InitializeClass(NoneMember)

noneMember = NoneMember()

def cloneMember(member):
    return Member(userid=member.userid(),
                  fullname=member.fullname(),
                  email=member.email(),
                  is_approved=member.is_approved())

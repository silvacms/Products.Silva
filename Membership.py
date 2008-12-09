from zope.interface import implements
from Products.SilvaViews.ViewRegistry import ViewAttribute

# some common classes used by Membership implementations
from AccessControl import ClassSecurityInfo
import Globals
from Globals import Persistent
import SilvaPermissions
import Acquisition

from interfaces import IMember

class Member(Persistent, Acquisition.Implicit):
    implements(IMember)

    security = ClassSecurityInfo()

    # allow edit view on this object
    edit = ViewAttribute('edit', 'tab_edit')

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

    def extra(self, name):
        """Extra information.
        """
        return None

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'editor')
    def editor(self):
        """Return the preferred editor"""
        return 'field_editor'

    security.declarePrivate('allowed_roles')
    def allowed_roles(self):
        return []

Globals.InitializeClass(Member)

class CachedMember(Persistent, Acquisition.Implicit):
    """A member object returned by cloneMember
    """

    implements(IMember)

    security = ClassSecurityInfo()

    def __init__(self, userid, fullname, email,
                 is_approved, editor, allowed_roles,
                 meta_type='Silva Simple Member'):
        self.id = userid
        self._fullname = fullname
        self._email = email
        self._is_approved = is_approved
        self._editor = editor
        self._allowed_roles = allowed_roles
        self._meta_type = meta_type

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'userid')
    def userid(self):
        """Returns the userid
        """
        return self.id

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fullname')
    def fullname(self):
        """Returns the full name
        """
        return self._fullname

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'email')
    def email(self):
        """Returns the e-mail address
        """
        return self._email

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_approved')
    def is_approved(self):
        """Returns 0
        """
        return self._is_approved

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'extra')
    def extra(self, name):
        """Extra information.
        """
        # fall back on actual member object, don't cache
        return self.service_members.get_member(self.id).extra(name)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'editor')
    def editor(self):
        """Return the preferred editor"""
        return self._editor

    security.declarePrivate('allowed_roles')
    def allowed_roles(self):
        """Return roles that that user can get"""
        return self._allowed_roles

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'meta_type')
    def meta_type(self):
        """Return meta_type of user object."""
        return self._meta_type


class NoneMember(Persistent, Acquisition.Implicit):
    implements(IMember)

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
        return 'unknown'

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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'extra')
    def extra(self, name):
        """Extra information.
        """
        return None

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'editor')
    def editor(self):
        """Return the preferred editor"""
        return 'field_editor'

    security.declarePrivate('allowed_roles')
    def allowed_roles(self):
        """Retune roles that that user can get"""
        return []

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'meta_type')
    def meta_type(self):
        """Return meta_type of user object."""
        return "Silva Simple Member"



Globals.InitializeClass(NoneMember)

noneMember = NoneMember()

def cloneMember(member):
    if member is None:
        return NoneMember()
    return CachedMember(userid=member.userid(),
                        fullname=member.fullname(),
                        email=member.email(),
                        is_approved=member.is_approved(),
                        editor=member.editor(),
                        allowed_roles=member.allowed_roles(),
                        meta_type=member.meta_type)

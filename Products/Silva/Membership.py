# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Persistence import Persistent
import Acquisition

from Products.Silva import SilvaPermissions

from silva.core.interfaces import IMember
from zope.interface import implements


class Member(Persistent, Acquisition.Implicit):
    implements(IMember)

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

    def extra(self, name):
        """Extra information.
        """
        return None

    security.declarePrivate('allowed_roles')
    def allowed_roles(self):
        return []

InitializeClass(Member)


class CachedMember(Persistent, Acquisition.Implicit):
    """A member object returned by cloneMember
    """
    implements(IMember)

    security = ClassSecurityInfo()

    def __init__(self, userid, fullname, email,
                 is_approved, allowed_roles,
                 meta_type='Silva Simple Member'):
        self.id = userid
        self._fullname = fullname
        self._email = email
        self._is_approved = is_approved
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
        member = self.service_members.get_member(self.id)
        if member is not None:
            # the member might not exist anymore
            return member.extra(name)
        return None

    security.declarePrivate('allowed_roles')
    def allowed_roles(self):
        """Return roles that that user can get"""
        return self._allowed_roles

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'meta_type')
    @property
    def meta_type(self):
        """Return meta_type of user object."""
        return self._meta_type

InitializeClass(CachedMember)


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

    security.declarePrivate('allowed_roles')
    def allowed_roles(self):
        """Retune roles that that user can get"""
        return []

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'meta_type')
    def meta_type(self):
        """Return meta_type of user object."""
        return "Silva Simple Member"


InitializeClass(NoneMember)

noneMember = NoneMember()

def cloneMember(member):
    if member is None:
        return NoneMember()
    return CachedMember(userid=member.userid(),
                        fullname=member.fullname(),
                        email=member.email(),
                        is_approved=member.is_approved(),
                        allowed_roles=member.allowed_roles(),
                        meta_type=member.meta_type)

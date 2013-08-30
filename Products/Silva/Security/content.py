# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from App.class_init import InitializeClass

from five import grok
from zope.component import getUtility

# Silva
from Products.Silva.Membership import noneMember
from Products.Silva import SilvaPermissions as permissions

from silva.core.interfaces import ISecurity
from silva.core.services.interfaces import IMemberService


class Security(object):
    """Provide support for author and creator information.
    """
    grok.implements(ISecurity)
    security = ClassSecurityInfo()

    _last_author_userid = None
    _last_author_info = None

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_creator_info')
    def get_creator_info(self):
        owner = self.getOwner()
        if owner is not None:
            identifier = self.getOwner().getId()
            if identifier:
                return getUtility(IMemberService).get_cached_member(
                    identifier, location=self)
        return noneMember.__of__(self)

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_last_author_info')
    def get_last_author_info(self):
        info = getattr(self, '_last_author_info', None)
        if info is None:
            return noneMember.__of__(self)
        return info.__of__(self)

    security.declareProtected(
        permissions.ChangeSilvaContent, 'set_last_author_info')
    def set_last_author_info(self, user):
        self._last_author_userid = user.userid()
        self._last_author_info = aq_base(user)


InitializeClass(Security)

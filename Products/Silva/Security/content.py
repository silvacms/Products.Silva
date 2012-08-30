# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base
from App.class_init import InitializeClass
from DateTime import DateTime

from zope.component import getUtility
from five import grok

# Silva
from Products.Silva.Membership import noneMember
from Products.Silva import SilvaPermissions as permissions
from Products.SilvaMetadata.interfaces import IMetadataService

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
        user_id = self.getOwner().getId()
        if not user_id:
            return noneMember.__of__(self)
        return getUtility(IMemberService).get_cached_member(
            user_id, location=self)

    security.declareProtected(
        permissions.AccessContentsInformation, 'get_last_author_info')
    def get_last_author_info(self):
        info = getattr(self, '_last_author_info', None)
        if info is None:
            return noneMember.__of__(self)
        return info.__of__(self)

    security.declareProtected(
        permissions.ChangeSilvaContent, 'update_last_author_info')
    def update_last_author_info(self):
        user_id = getSecurityManager().getUser().getId()
        user = getUtility(IMemberService).get_cached_member(
            user_id, location=self)
        self._last_author_userid = user_id
        self._last_author_info = aq_base(user)
        binding = getUtility(IMetadataService).getMetadata(self)
        if binding is None or binding.read_only:
            return
        now = DateTime()
        binding.setValues('silva-extra', {'modificationtime': now})


InitializeClass(Security)

# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.16 $
# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
# Silva 
import SilvaPermissions
# misc
import helpers

from interfaces import IPublishable, IContent, IVersioning, IContainer

class Publishable:
    """Mixin class that can be provided to implement the Publishable
    interface.
    """
    security = ClassSecurityInfo()
        
    __implements__ = IPublishable

    _active_flag = 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'activate')
    def activate(self):
        if not self.can_activate():
            return
        self._active_flag = 1
        # refresh container of parent (may be parent itself)
        # we use parent so we don't get *this* publishable container
        self.aq_parent.get_container()._refresh_ordered_ids(self)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'deactivate')
    def deactivate(self):
        if not self.can_deactivate():
            return
        # we can deactivate, but we should unapprove everything that
        # is approved
        helpers.unapprove_helper(self)
        # now set the flag
        self._active_flag = 0
        # refresh container of parent (may be parent itself)
        # we use parent so we don't get *this* publishable container
        self.aq_parent.get_container()._refresh_ordered_ids(self)
        
    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_active')
    def is_active(self):
        return self._active_flag

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'can_activate')
    def can_activate(self):
        return not self._active_flag

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'can_deactivate')
    def can_deactivate(self):
        if not self._active_flag:
            return 0
        # can't deactivate default
        if IContent.isImplementedBy(self) and self.is_default():
            return 0
        # can't deactivate something published
        if self.is_published():
            return 0
        return 1

    # FIXME: perhaps make this less public?
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_published')
    def is_published(self):
        if IVersioning.isImplementedBy(self):
            return self.is_version_published()
        else:
            # FIXME: should always be published if no versioning supported?
            return 0

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_approved')
    def is_approved(self):
        if IVersioning.isImplementedBy(self):
            return self.is_version_approved()
        else:
            # never be approved if there is no versioning
            return 0
        
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'can_approve')
    def can_approve(self):
        """Return true if we can approve version.
        NOTE: this method is defined by the Versioning interface, but
        this is the default implementation for versioned publishables.
        """
        # if this object or any of its containers is inactive, can't approve it        
        if not self.is_active():
            return 0
        # check all containers to see if they are inactive as well
        object = self.aq_parent
        while IContainer.isImplementedBy(object):
            if not object.is_active():
                return 0
            object = object.aq_parent
        # all containers were active, so we can indeed approve
        return 1

InitializeClass(Publishable)

# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from zope.component import queryUtility
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from App.class_init import InitializeClass
from OFS.interfaces import IObjectWillBeMovedEvent

# Silva
from Products.Silva import SilvaPermissions
from silva.core.interfaces import IRoot
from silva.core.interfaces import IQuotaContainer, IQuotaObject
from silva.core.interfaces import IContentImporter
from silva.core.services.interfaces import IExtensionService


class QuotaObject(object):
    """A content that uses some of the site quota
    """
    security = ClassSecurityInfo()
    _old_size = 0               # Old size of the object.

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_quota_usage')
    def get_quota_usage(self):
        return -1

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'update_quota')
    def update_quota(self):
        parent = aq_parent(self)
        if IQuotaContainer.providedBy(parent):
            service = queryUtility(IExtensionService)
            if service is None:
                return
            verify = service.get_quota_subsystem_status()
            if verify is None:
                return

            # Every content must be inside a container (unless they
            # are inside an image ...).
            new_size = self.get_quota_usage()
            if new_size < 0:
                # Broken quota usage
                return
            delta = new_size - self._old_size
            if delta:
                parent.update_used_space(delta, verify)
                self._old_size = new_size

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'reset_quota')
    def reset_quota(self):
        self._old_size = max(0, self.get_quota_usage())
        return self._old_size

InitializeClass(QuotaObject)


class QuotaContainer(object):
    """A container that aggregate multiple quota objects
    """
    security = ClassSecurityInfo()
    used_space = 0

    def _verify_quota(self):
        # Hook to check quota. Do nothing by default.
        pass

    security.declarePrivate('update_used_space')
    def update_used_space(self, delta, verify=True):
        if IContentImporter.providedBy(aq_parent(self)):
            aq_inner(self).update_used_space(delta, verify)
            return

        self.used_space += delta
        # If we add stuff, check we're not over quota.
        if verify and delta > 0:
            self._verify_quota()

        if not IRoot.providedBy(self):
            container = aq_parent(self)
            if container is not None:
                container.update_used_space(delta, verify)

InitializeClass(QuotaContainer)


@grok.subscribe(IQuotaObject, IObjectWillBeMovedEvent)
def content_moved_update_quota(content, event):
    """Event called on a quotable when they are moved to update quota
    on parents folders.
    """
    if content != event.object or event.newParent is event.oldParent:
        return

    service = queryUtility(IExtensionService)
    if service is None:
        return

    verify = service.get_quota_subsystem_status()
    if verify is None:
        # Quota accouting is disabled
        return

    size = content.get_quota_usage()
    if not size or size < 0:
        return

    if event.oldParent and IQuotaContainer.providedBy(event.oldParent):
        event.oldParent.update_used_space(-size, verify)
    if event.newParent and IQuotaContainer.providedBy(event.newParent):
        event.newParent.update_used_space(size, verify)


@grok.subscribe(IQuotaContainer, IObjectWillBeMovedEvent)
def container_moved_update_used_space(content, event):
    """Event called on folder, when they are moved, we want to update
    the quota on parents folders.
    """
    if content != event.object or IRoot.providedBy(content):
        # Root is being destroyed, we don't care about quota anymore.
        return

    if event.newParent is event.oldParent:
        # For rename event, we don't need to do something.
        return

    service = queryUtility(IExtensionService)
    if service is None:
        return
    verify = service.get_quota_subsystem_status()
    if verify is None:
        # Quota accounting is disabled.
        return

    size = content.used_space
    if not size or size < 0:
        return
    if event.oldParent and IQuotaContainer.providedBy(event.oldParent):
        event.oldParent.update_used_space(-size, verify)
    if event.newParent and IQuotaContainer.providedBy(event.newParent):
        event.newParent.update_used_space(size, verify)


@grok.subscribe(IQuotaObject, IObjectCreatedEvent)
def update_quota_created(content, event):
    content.update_quota()


@grok.subscribe(IQuotaObject, IObjectModifiedEvent)
def update_quota_modified(content, event):
    content.update_quota()

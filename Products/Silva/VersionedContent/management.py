# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator

from five import grok

from DateTime import DateTime
from datetime import datetime

from silva.core.interfaces import IVersion
from silva.core.interfaces import IVersionedContent
from silva.core.interfaces import IPublicationWorkflow, PublicationWorkflowError
from silva.translations import translate as _


class VersionedContentPublicationWorkflow(grok.Adapter):
    grok.context(IVersionedContent)
    grok.implements(IPublicationWorkflow)
    grok.provides(IPublicationWorkflow)

    def new_version(self):
        if self.context.get_unapproved_version() is not None:
            raise PublicationWorkflowError(
                _("This content already has a new version."))
        self.context.create_copy()
        return True

    def request_approval(self, message):
        # XXX add checkout publication datetime
        # set_unapproved_version_publication_datetime(DateTime())
        if self.context.get_unapproved_version() is None:
            raise PublicationWorkflowError(
                _('There is no unapproved version.'))
        if self.context.is_approval_requested():
            raise PublicationWorkflowError(
                _('Approval has already been requested.'))
        self.context.request_version_approval(message)
        return True

    def _check_withdraw_or_reject(self):
        if self.context.get_unapproved_version() is None:
            if self.context.get_public_version() is not None:
                raise PublicationWorkflowError(
                    _("This content is already public."))
            else:
                raise PublicationWorkflowError(
                    _("This content is already approved."))
        if not self.context.is_approval_requested():
            raise PublicationWorkflowError(
                _("No request for approval is pending for this content."))

    def withdraw_request(self, message):
        self._check_withdraw_or_reject()
        self.context.withdraw_version_approval(message)
        return True

    def reject_request(self, message):
        self._check_withdraw_or_reject()
        self.context.reject_version_approval(message)
        return True

    def revoke_approval(self):
        if self.context.get_approved_version():
            self.context.unapprove_version()
            return True
        raise PublicationWorkflowError(
            _(u"This content is not approved."))

    def approve(self, time=None):
        if time is None:
            time = DateTime()
        elif isinstance(time, datetime):
            time = DateTime(time)
        if self.context.get_unapproved_version() is None:
            raise PublicationWorkflowError(
                _("There is no unapproved version to approve."))
        self.context.set_unapproved_version_publication_datetime(time)
        self.context.approve_version()
        return True

    def publish(self, time=None):
        # Do the same job than approve, but works on closed content as
        # well.
        if not self.context.get_unapproved_version():
            if self.context.is_published():
                raise PublicationWorkflowError(
                    _("There is no unapproved version to approve."))
            self.context.create_copy()
        self.approve(time)
        return True

    def close(self):
        if self.context.get_public_version() is None:
            raise PublicationWorkflowError(
                _("There is no public version to close"))
        self.context.close_version()
        return True

    def get_versions(self, sort_attribute='id'):
        versions = filter(IVersion.providedBy, self.context.objectValues())
        if sort_attribute == 'id':
            versions.sort(key=lambda a: int(a.id))
        elif sort_attribute:
            versions.sort(key=operator.attrgetter(sort_attribute))
        return versions


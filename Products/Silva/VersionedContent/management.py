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
from silva.core.interfaces import IPublicationWorkflow, PublicationError
from silva.translations import translate as _


class VersionedContentPublicationWorkflow(grok.Adapter):
    grok.context(IVersionedContent)
    grok.implements(IPublicationWorkflow)
    grok.provides(IPublicationWorkflow)

    def new_version(self):
        self.context.create_copy()
        return True

    def request_approval(self, message=None):
        if message is None:
            message = u"Request immediate publication of this content. " + \
                u"(automatically generated message)."
        self.context.request_version_approval(message)
        return True

    def withdraw_request(self, message=None):
        if message is None:
            message = u"Approval was withdrawn " + \
                u"(automatically generated message)."
        self.context.withdraw_version_approval(message)
        return True

    def reject_request(self, message=None):
        if message is None:
            message = u"Approval was rejected " +\
                u"(automatically generated message)."
        self.context.reject_version_approval(message)
        return True

    def revoke_approval(self):
        self.context.unapprove_version()
        return True

    def approve(self, time=None):
        if self.context.get_unapproved_version() is None:
            raise PublicationError(
                _("There is no unapproved version to approve."),
                self.context)
        if time is not None:
            if isinstance(time, datetime):
                time = DateTime(time)
            self.context.set_unapproved_version_publication_datetime(time)
        elif self.context.get_unapproved_version_publication_datetime() is None:
            self.context.set_unapproved_version_publication_datetime(DateTime())
        self.context.approve_version()
        return True

    def publish(self):
        # Do the same job than approve, but works on closed content as
        # well.
        if not self.context.get_unapproved_version():
            if self.context.is_published():
                raise PublicationError(
                    _("There is no unapproved version to approve."),
                    self.context)
            self.context.create_copy()
        current = self.context.get_unapproved_version_publication_datetime()
        if current is None or current.isFuture():
            # If the publication date is in the future, set it correct to now.
            self.context.set_unapproved_version_publication_datetime(DateTime())
        self.context.approve_version()
        return True

    def close(self):
        self.context.close_version()
        return True

    def get_versions(self, sort_attribute='id'):
        versions = filter(IVersion.providedBy, self.context.objectValues())
        if sort_attribute == 'id':
            versions.sort(key=lambda a: int(a.id))
        elif sort_attribute:
            versions.sort(key=operator.attrgetter(sort_attribute))
        return versions


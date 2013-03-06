# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from silva.core import interfaces

from Products.SilvaMetadata.Index import MetadataCatalogingAttributes


class CatalogingAttributes(MetadataCatalogingAttributes):
    grok.context(interfaces.ISilvaObject)

    def publication_status(self):
        return 'public'

    def content_intid(self):
        return getUtility(IIntIds).register(self.context)


class CatalogingAttributesPublishable(CatalogingAttributes):
    grok.context(interfaces.IPublishable)

    def publication_status(self):
        if self.context.is_published():
            return 'public'
        if self.context.is_approved():
            return 'approved'
        return 'unapproved'


class CatalogingAttributesVersion(CatalogingAttributes):
    grok.context(interfaces.IVersion)

    def content_intid(self):
        return getUtility(IIntIds).register(self.context.get_silva_object())

    def publication_status(self):
        """Returns the status of the current version
        Can be 'unapproved', 'approved', 'public', 'last_closed' or 'closed'
        """
        content = self.context.get_silva_object()
        status = None
        unapproved_version = content.get_unapproved_version()
        approved_version = content.get_approved_version()
        public_version = content.get_public_version()
        previous_versions = content.get_previous_versions()
        if unapproved_version and unapproved_version == self.context.id:
            status = "unapproved"
        elif approved_version and approved_version == self.context.id:
            status = "approved"
        elif public_version and public_version == self.context.id:
            status = "public"
        else:
            if previous_versions and previous_versions[-1] == self.context.id:
                status = "last_closed"
            elif self.context.id in previous_versions:
                status = "closed"
            else:
                # this is a completely new version not even registered
                # with the machinery yet
                status = 'unapproved'
        return status


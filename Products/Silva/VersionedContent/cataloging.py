# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok

from Acquisition import aq_base

from OFS.interfaces import IObjectClonedEvent
from silva.core.interfaces import IVersionedContent, IVersion
from silva.core.services.catalog import Cataloging
from silva.core.services.interfaces import ICataloging, ICatalogingAttributes
from silva.core.interfaces.events import IContentClosedEvent
from silva.core.interfaces.events import IContentPublishedEvent
from silva.core.interfaces.events import IApprovalEvent


class VersionedContentCataloging(Cataloging):
    """Cataloging support for versioned content.
    """
    grok.context(IVersionedContent)

    def get_indexable_versions(self):
        version_ids = [
            self.context.get_next_version(),
            self.context.get_public_version()]
        for version_id in version_ids:
            if version_id is None:
                continue
            if hasattr(aq_base(self.context), version_id):
                yield getattr(self.context, version_id)

    def index(self, indexes=None, with_versions=True):
        if self._catalog is None:
            return
        super(VersionedContentCataloging, self).index(indexes=indexes)
        if with_versions:
            for version in self.get_indexable_versions():
                attributes = ICatalogingAttributes(version)
                path = '/'.join((self._path, version.getId(),))
                self._catalog.catalog_object(attributes, path)

    def unindex(self, with_versions=True):
        if self._catalog is None:
            return
        super(VersionedContentCataloging, self).unindex()
        if with_versions:
            for version in self.get_indexable_versions():
                path = '/'.join((self._path, version.getId(),))
                self._catalog.uncatalog_object(path)


@grok.subscribe(IVersion, IObjectClonedEvent)
def catalog_version(version, event):
    ICataloging(version).index()
    ICataloging(version.get_content()).index(with_versions=False)


@grok.subscribe(IVersion, IApprovalEvent)
@grok.subscribe(IVersion, IContentPublishedEvent)
def recatalog_version(version, event):
    ICataloging(version).index()
    ICataloging(version.get_content()).index(with_versions=False)


@grok.subscribe(IVersion, IContentClosedEvent)
def uncatalog_version(version, event):
    ICataloging(version).unindex()
    ICataloging(version.get_content()).unindex(with_versions=False)

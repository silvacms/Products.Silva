# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok

from Acquisition import aq_base

from OFS.interfaces import IObjectClonedEvent
from silva.core.interfaces import IVersionedContent, IVersion
from silva.core.services.catalog import Cataloging, catalog_queue
from silva.core.services.interfaces import ICataloging
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
        super(VersionedContentCataloging, self).index(indexes=indexes)
        if with_versions:
            for version in self.get_indexable_versions():
                catalog_queue.index(version, indexes)

    def reindex(self, indexes=None, with_versions=True):
        super(VersionedContentCataloging, self).index(indexes=indexes)
        if with_versions:
            for version in self.get_indexable_versions():
                catalog_queue.index(version, indexes)

    def unindex(self, with_versions=True):
        if with_versions:
            for version in self.get_indexable_versions():
                catalog_queue.unindex(version)
        super(VersionedContentCataloging, self).unindex()



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

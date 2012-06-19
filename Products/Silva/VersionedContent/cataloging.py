# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok

from Acquisition import aq_base

from silva.core.interfaces import IVersionedObject
from silva.core.services.catalog import Cataloging, catalog_queue


class VersionedContentCataloging(Cataloging):
    """Cataloging support for versioned content.
    """
    grok.context(IVersionedObject)

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
        super(VersionedContentCataloging, self).reindex(indexes=indexes)
        if with_versions:
            for version in self.get_indexable_versions():
                catalog_queue.reindex(version, indexes)

    def unindex(self, with_versions=True):
        if with_versions:
            for version in self.get_indexable_versions():
                catalog_queue.unindex(version)
        super(VersionedContentCataloging, self).unindex()

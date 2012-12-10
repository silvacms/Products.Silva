# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import uuid

# Zope 3
from five import grok
from zope.component import getUtility

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem

# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.interfaces import IIndexEntries, IIndexer
from silva.core.interfaces import IContent, IPublishable
from silva.core.references.interfaces import IReferenceService, IReferenceValue
from silva.core.references.reference import ReferenceValue
from silva.core.services.utils import advanced_walk_silva_tree
from silva.translations import translate as _

REFERENCE_TAG = u'indexer'


class IndexerReferenceValue(ReferenceValue):

    def cleanup(self):
        source = self.source
        if source is not None and IIndexer.providedBy(source):
            source._remove_reference_related_entries(self)


class Indexer(Content, SimpleItem):
    __doc__ = _("""Indexes can be created that function like an index in the
       back of a book. References must first be marked by placing index
       codes in text (these codes will also export to print formats).
       Indexers cascade downwards, indexing all index items in the current
       and underlying folders and publications (note that it only indexes
       documents that are published).
    """)
    security = ClassSecurityInfo()

    meta_type = "Silva Indexer"
    grok.implements(IIndexer)
    silvaconf.icon('www/silvaindexer.png')

    def __init__(self, id):
        super(Indexer, self).__init__(id)
        # index format:
        # {index_name: (obj_id, obj_title),}
        self._index = {}

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_index_names')
    def get_index_names(self):
        """Returns a list of all index entry names in the index, sorted
        alphabetically.
        """
        result = self._index.keys()
        result.sort(key=lambda i: i.lower())
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_index_entry')
    def get_index_entry(self, entry):
        """Returns a list of (title, path) tuples for an entry name in the
        index, sorted alphabetically on title
        """
        get_references = getUtility(IReferenceService).get_references_from
        contents = dict(
            map(
                lambda r: (r.tags[1], r.target),
                filter(
                    lambda r: r.tags[0] == REFERENCE_TAG,
                    get_references(self, name=REFERENCE_TAG))))

        result = [(title, contents.get(path), name)
                  for path, (name, title) in
                  self._index.get(entry, {}).items()]
        result.sort(key=lambda i: i[0].lower())
        return result

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'update')
    def update(self):
        """Update the index.
        """
        result = {}
        want_next = None
        service = getUtility(IReferenceService)
        walker = advanced_walk_silva_tree(self.get_container(), IPublishable)

        # get tree of all subobjects
        while True:
            try:
                content = walker.send(want_next)
            except StopIteration:
                break
            want_next = content.is_published()
            if not want_next:
                continue

            if IContent.providedBy(content) and content.is_default():
                # We skip default contents.
                continue

            indexable = IIndexEntries(content)
            title = indexable.get_title()
            if not title:
                continue
            indexes = indexable.get_entries()
            if not indexes:
                continue

            references = service.get_references_between(
                self, content, name=REFERENCE_TAG)
            try:
                reference = references.next()
            except StopIteration:
                reference_name = unicode(uuid.uuid1())
                reference = service.new_reference(
                    self, name=REFERENCE_TAG, factory=IndexerReferenceValue)
                reference.set_target(content)
                reference.add_tag(reference_name)
            else:
                if len(reference.tags) > 1:
                    reference_name = reference.tags[1]
                else:
                    # Upgrade existing references
                    reference_name = unicode(uuid.uuid1())
                    reference.add_tag(reference_name)
            for name, label in indexes:
                if label:
                    entry = result.setdefault(label, {})
                    entry[reference_name] = (name, title)

        self._index = result

    def _remove_reference_related_entries(self, reference):
        if IReferenceValue.providedBy(reference):
            reference_name = reference.tags[1]
        else:
            reference_name = reference
        for indexes in self._index.itervalues():
            if indexes.has_key(reference_name):
                del indexes[reference_name]

InitializeClass(Indexer)



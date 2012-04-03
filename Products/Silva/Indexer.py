# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from zope.event import notify
from zope.component import getUtility
from zope.traversing.browser import absoluteURL
from zope.lifecycleevent import ObjectModifiedEvent

# Zope 2
from AccessControl import ClassSecurityInfo
from AccessControl.security import checkPermission
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem

# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.smi.content import IEditScreen
from silva.core.interfaces import IIndexEntries, IIndexer
from silva.core.interfaces import IContent, IPublishable
from silva.core.references.interfaces import IReferenceService, IReferenceValue
from silva.core.references.reference import WeakReferenceValue
from silva.core.services.utils import advanced_walk_silva_tree
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from zeam.form import silva as silvaforms


class IndexerReferenceValue(WeakReferenceValue):

    def __init__(self, *args, **kwargs):
        super(IndexerReferenceValue, self).__init__(*args, **kwargs)
        if not IIndexer.providedBy(self.source):
            raise TypeError('Indexer only accepts IIndexer as source')

    def cleanup(self):
        source = super(IndexerReferenceValue, self).cleanup()
        if source is not None:
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
        result = [(title, path, name) for path, (name, title) in
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
        reference_service = getUtility(IReferenceService)
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
            indexes = indexable.get_entries()
            if not indexes:
                continue

            title = indexable.get_title()
            references = reference_service.get_references_between(
                self, content, name="indexer")
            try:
                reference = references.next()
            except StopIteration:
                reference = reference_service.new_reference(
                    self, name=u"indexer", factory=IndexerReferenceValue)
                reference.set_target(content)
            for indexName, indexTitle in indexes:
                result.setdefault(indexTitle, {})[reference.__name__] = \
                    (indexName, title)

        self._index = result

    def _remove_reference_related_entries(self, reference):
        if IReferenceValue.providedBy(reference):
            reference_name = reference.__name__
        else:
            reference_name = reference
        for indexes in self._index.itervalues():
            if indexes.has_key(reference_name):
                del indexes[reference_name]

InitializeClass(Indexer)


class IndexerAddForm(silvaforms.SMIAddForm):
    """Add form for Silva indexer.
    """
    grok.context(IIndexer)
    grok.name(u"Silva Indexer")


class IndexerEditForm(silvaforms.SMIForm):
    """Edit form for an indexer. There is not that much to edit however.
    """
    grok.context(IIndexer)
    grok.require('silva.ReadSilvaContent')
    grok.implements(IEditScreen)

    label = _("Update Silva Indexer")
    description = _(
        u"An index is not editable. "
        u"However, you can update the index to include recent added content.")
    actions = silvaforms.Actions(silvaforms.CancelEditAction())

    def update_index_available(self):
        return checkPermission('silva.ChangeSilvaContent', self.context)

    @silvaforms.action(
        _(u"Update index"),
        accesskey=u"u",
        available=update_index_available,
        description=_(u"Update index to include recent added content"))
    def update_index(self):
        self.context.update()
        notify(ObjectModifiedEvent(self.context))
        self.send_message(
            _(u"Index content have been successfully updated."),
            type="feedback")


class IndexerView(silvaviews.View):
    """View on indexer objects.
    """
    grok.context(IIndexer)

    def update(self):
        cache = {}
        references = getUtility(IReferenceService).references

        def resolver(cid):
            if cid in cache:
                return cache[cid]
            reference = references.get(cid, None)
            if reference is not None:
                url = absoluteURL(reference.target, self.request)
                cache[cid] = url
                return url
            return ''

        self.__resolver = resolver

    def links(self, links):
        for title, cid, name in links:
            url = self.__resolver(cid)
            yield '<a class="indexer" href="%s#%s">%s</a>' % (url, name, title)



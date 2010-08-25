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
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem

# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.smi.interfaces import IEditTabIndex
from silva.core.interfaces import IIndexable, IIndexer
from silva.core.references.interfaces import IReferenceService, IReferenceValue
from silva.core.references.reference import WeakReferenceValue
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from zeam.form import silva as silvaforms


class IndexerReferenceValue(WeakReferenceValue):

    def __init__(self, *args, **kwargs):
        super(IndexerReferenceValue, self).__init__(*args, **kwargs)
        if not IIndexer.providedBy(self.source):
            raise TypeError('Indexer only accepts IIndexer as source')

    def cleanup(self):
        super(IndexerReferenceValue, self).cleanup()
        self.source._remove_reference_related_entries(self)


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
                              'getIndexNames')
    def getIndexNames(self):
        """Returns a list of all index entry names in the index, sorted
        alphabetically.
        """
        result = [(item.lower(), item) for item in self._index.keys()]
        result.sort()
        result = [second for first, second in result]
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'getIndexEntry')
    def getIndexEntry(self, indexTitle):
        """Returns a list of (title, path) tuples for an entry name in the
        index, sorted alphabetically on title
        """
        result = []
        for path, (name, title) in self._index[indexTitle].items():
            result.append((title.lower(), title, path, name,))
        result.sort()
        result = [(title, path, name) for _, title, path, name in result]
        return result

    def _getIndexables(self):
        """Returns all indexables from the container containing this
        Indexer object, including and its subcontainers
        """
        container = self.get_container()
        default_obj = container.get_default()
        result = []
        if default_obj:
            result.append(default_obj)
        result.extend([item for i, item in container.get_public_tree_all()])
        return result

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'update')
    def update(self):
        """Update the index.
        """
        result = {}
        reference_service = getUtility(IReferenceService)

        # get tree of all subobjects
        for content in self._getIndexables():
            indexable = IIndexable(content)
            indexes = indexable.getIndexes()
            if not indexes:
                continue

            title = indexable.getTitle()
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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_deletable')
    def is_deletable(self):
        """always deletable"""
        return 1

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """return 1 so the title can be set"""
        return 1


InitializeClass(Indexer)


class IndexerAddForm(silvaforms.SMIAddForm):
    """Add form for Silva indexer.
    """
    grok.context(IIndexer)
    grok.name(u"Silva Indexer")


class IndexerEditForm(silvaforms.SMIForm):
    """Edit form for an indexer. There is not that much to edit however.
    """
    grok.name('tab_edit')
    grok.context(IIndexer)
    grok.implements(IEditTabIndex)

    description = _(
        u"An index is not editable. "
        u"However, you can update the index to include recent added content.")
    actions = silvaforms.Actions(silvaforms.CancelEditAction())

    @silvaforms.action(
        _(u"update index"),
        accesskey=u"u",
        description=_(u"Update index to include recent added content: alt-u"))
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



# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import implements

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem

# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.interfaces import IIndexable, IIndexer
from silva.core.views import views as silvaviews
from silva.core.forms import z3cforms as silvaz3cforms
from zeam.form.silva.form import SMIAddForm

from silva.translations import translate as _


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
    implements(IIndexer)
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
        result = [
            (title, path, name) for title_lowercase, title, path, name in result]
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
        resolver = getUtility(IIntIds)
        # get tree of all subobjects
        for object in self._getIndexables():
            indexable = IIndexable(object)
            indexes = indexable.getIndexes()
            if not indexes:
                continue

            title = indexable.getTitle()
            obj_id = resolver.register(object)
            for indexName, indexTitle in indexes:
                result.setdefault(indexTitle, {})[obj_id] = (indexName, title)
        self._index = result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_deletable')
    def is_deletable(self):
        """always deletable"""
        return 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_cacheable')
    def is_cacheable(self):
        """always cacheable"""
        return 1

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """return 1 so the title can be set"""
        return 1

InitializeClass(Indexer)

class IndexerAddForm(SMIAddForm):
    """Add form for Silva indexer.
    """
    silvaconf.name(u"Silva Indexer")


class IndexerView(silvaviews.View):
    """View on indexer objects.
    """

    silvaconf.context(IIndexer)

    def update(self):
        self.resolver = getUtility(IIntIds)

    def render_links(self, links):
        result = []
        for title, cid, name in links:
            # XXX: This is sub-optimal
            url = self.resolver.getObject(cid).absolute_url()
            result.append(
                '<a class="indexer" href="%s#%s">%s</a>' % (
                    url, name, title))
        return '<br />'.join(result)

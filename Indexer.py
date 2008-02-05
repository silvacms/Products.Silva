# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.25 $
from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
import OFS
from OFS.SimpleItem import SimpleItem
import zLOG
# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit
from Products.Silva import mangle
from Products.Silva.i18n import translate as _
from Products.Silva.adapters.interfaces import IIndexable

from interfaces import IContent, IContainer, IPublication
    
icon = "www/silvaindexer.png"

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

    implements(IContent)

    def __init__(self, id, title):
        Indexer.inheritedAttribute('__init__')(self, id, title)
        # index format:
        # {index_name: (obj_path, obj_title),}
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
    def getIndexEntry(self, name):
        """Returns a list of (title, path) tuples for an entry name in the
        index, sorted alphabetically on title
        """
        result = []
        for path, title in self._index[name].items():
            result.append((title.lower(), title, path,))
        result.sort()
        result = [(title, path) for title_lowercase, title, path in result]
        return result
    
    def _getIndexables(self):
        """Returns all indexables from the container containing this Indexer object,
        including and its subcontainers
        """
        result = []
        return [item for i, item in self.get_container().get_public_tree_all()]
                      
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'update')
    def update(self):
        """Update the index.
        """      
        result = {}
        # get tree of all subobjects
        for object in self._getIndexables():
            indexable = IIndexable(object)
            indexes = indexable.getIndexes()
            if not indexes:
                continue

            title = indexable.getTitle()
            path = indexable.getPath()
            for indexName in indexes:
                result.setdefault(indexName, {})[path] = title
        self._index = result

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

manage_addIndexerForm = PageTemplateFile("www/indexerAdd", globals(),
                                         __name__='manage_addIndexerForm')

def manage_addIndexer(self, id, title, REQUEST=None):
    """Add an indexer."""
    if not mangle.Id(self, id).isValid():
        return
    object = Indexer(id, title)
    self._setObject(id, object)
    
    indexer = self._getOb(id)
    indexer.set_title(title)

    add_and_edit(self, id, REQUEST)
    return ''


# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.5 $
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
import OFS
from OFS.SimpleItem import SimpleItem
# Silva interfaces
from Products.Silva.IContent import IContent
# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions
# misc
from Products.Silva.helpers import add_and_edit
from IContainer import IContainer
# try to import xpath
try:
    from xml import xpath
    from xml.xpath.Context import Context
    XPATH_AVAILABLE = 1
except ImportError:
    XPATH_AVAILABLE = 0
    
icon = "www/silvageneric.gif"

class Indexer(Content, SimpleItem):
    """Indexes can be created that function like an index in the 
       back of a book. References must first be marked by placing index 
       codes in text (these codes will also export to print formats). 
       Indexers cascade downwards, indexing all index items in the current 
       and underlying publications (indexes only published documents).
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Indexer"

    __implements__ = IContent

    def __init__(self, id, title):
        Indexer.inheritedAttribute('__init__')(self, id, title)
        self._index = None

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_index')
    def get_index(self):
        """Get an index. Return None if there is no index.
        """
        return self._index

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'update_index')
    def update_index(self):
        """Update the index.
        """
        if not XPATH_AVAILABLE:
            print "Silva Indexer: cannot update index as xml.xpath not installed."
            return
        result = {}
        # get tree of all subobjects
        items = self._get_tree()
        # now go through all ParsedXML documents given as indexable and
        # index them
        for item in items:
            self._indexObject(result, item)
        # now massage into final index structure
        index = []
        names = result.keys()
        # case insensitive sort
        ci_names = [(name.lower(), name) for name in names]
        ci_names.sort()
        names = [name for name_lower, name in ci_names]
        for name in names:
            links = [(content.get_title(), url)
                     for url, content in result[name].items()]
            index.append((name, links))
        self._index = index

    def _indexObject(self, result, object):
        for doc in object.get_indexables():
            context = Context(doc.getDOM(), 0, 0)
            nodes = xpath.Evaluate('//index', context=context)
            for node in nodes:
                result.setdefault(node.getAttribute('name'), {})[
                    object.content_url()] = object.get_content()

    def _get_tree(self):
        l = []
        self._get_tree_helper(l, self.get_container())
        return l

    # XXX should be a helper method on folder that does this..
    def _get_tree_helper(self, l, item):
        default = item.get_default()
        if default is not None:
            l.append(default)
        for child in item.get_ordered_publishables():
            if IContainer.isImplementedBy(child):
                self._get_tree_helper(l, child)
            else:
                l.append(child)
                
InitializeClass(Indexer)

manage_addIndexerForm = PageTemplateFile("www/indexerAdd", globals(),
                                         __name__='manage_addIndexerForm')

def manage_addIndexer(self, id, title, REQUEST=None):
    """Add an indexer."""
    if not self.is_id_valid(id):
        return
    object = Indexer(id, title)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''


# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
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
from xml import xpath
from xml.xpath.Context import Context

icon = "www/silvageneric.gif"

class Index(Content, SimpleItem):
    """Index asset.
    """    
    security = ClassSecurityInfo()

    meta_type = "Silva Index"

    __implements__ = IContent

    def __init__(self, id, title):
        Index.inheritedAttribute('__init__')(self, id, title)
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
        result = {}
        # get status tree from folder by acquisition
        # XXX perhaps get_status_tree() should be renamed or some
        # new method should be created for this use
        # XXX does not index 'index' documents!
        items = self.get_status_tree()
        # now go through all ParsedXML documents given as indexable and
        # index them
        for ident, item in items:
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
                
InitializeClass(Index)

manage_addIndexForm = PageTemplateFile("www/indexAdd", globals(),
                                       __name__='manage_addIndexForm')

def manage_addIndex(self, id, title, REQUEST=None):
    """Add an index."""
    if not self.is_id_valid(id):
        return
    object = Index(id, title)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''


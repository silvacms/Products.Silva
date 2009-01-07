# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: AutoTOC.py,v 1.15 2006/01/24 16:14:12 faassen Exp $

from zope.interface import implements

# Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Persistence import Persistent
from OFS.SimpleItem import SimpleItem

# products
from Products.ParsedXML.ParsedXML import ParsedXML

# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions
from Products.Silva.i18n import translate as _
from Products.Silva.interfaces import IAutoTOC, IContainerPolicy
from Products.Silva.adapters import tocrendering

class AutoTOC(Content, SimpleItem):
    __doc__ = _("""This is a special document that automagically displays a
       table of contents. Usually it&#8217;s used as an &#8216;index&#8217;
       document. In that case the parent folder shows a table of contents
       when accessed (e.g. http://www.x.yz/silva/myFolder/).""")
    security = ClassSecurityInfo()

    meta_type = "Silva AutoTOC"

    implements(IAutoTOC)

    _toc_depth = -1

    def __init__(self, id):
        AutoTOC.inheritedAttribute('__init__')(self, id, 'Dummy Title')
        
    # ACCESSORS
    security.declareProtected(SilvaPermissions.View, 'is_cacheable')
    def is_cacheable(self):
        """Return true if this document is cacheable.
        That means the document contains no dynamic elements like
        code, toc, etc.
        """
        return 0

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'is_deletable')
    def is_deletable(self):
        """always deletable"""
        return 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'can_set_title')
    def can_set_title(self):        
        """always settable"""
        # XXX: we badly need Publishable type objects to behave right.
        return 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'set_toc_depth')
    def set_toc_depth(self, depth):
        self._toc_depth = depth
        
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'toc_depth')
    def toc_depth(self):
        """get the depth to which the toc will be rendered"""
        return self._toc_depth
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_tree')
    def render_tree(self, public=1,append_to_url=None):
        """Get adapter to render this autotoc's tree"""
        adapter = tocrendering.getTOCRenderingAdapter(self)
        return adapter.render_tree(public,
                                   append_to_url,
                                   toc_depth=self.toc_depth())

InitializeClass(AutoTOC)

def manage_addAutoTOC(self, id, title, depth=-1, REQUEST=None):
    """Add a autotoc."""
    if not mangle.Id(self, id).isValid():
        return
    object = AutoTOC(id)
    self._setObject(id, object)
    object = getattr(self, id)
    object.set_title(title)
    object.set_toc_depth(depth)
    add_and_edit(self, id, REQUEST)
    return ''

class AutoTOCPolicy(Persistent):

    implements(IContainerPolicy)

    def createDefaultDocument(self, container, title):
        container.manage_addProduct['Silva'].manage_addAutoTOC(
            'index', title)
        container.index.sec_update_last_author_info()

# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: AutoTOC.py,v 1.15 2006/01/24 16:14:12 faassen Exp $

from zope.interface import implements

# Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Persistence import Persistent
from OFS.SimpleItem import SimpleItem

# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions
from Products.Silva.i18n import translate as _
from silva.core.interfaces import IAutoTOC, IContainerPolicy
from Products.Silva.adapters import tocrendering

from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

class AutoTOC(Content, SimpleItem):
    __doc__ = _("""This is a special document type that automatically generates
       a Table of Contents. Usually it's used as the 'index' document of a
       folder. Then the parent folder displays a TOC when accessed (e.g.
       http://www.x.yz/silva/myFolder/). The AutoTOC can display any selection
       of Silva content types including assets.""")
    security = ClassSecurityInfo()

    meta_type = "Silva AutoTOC"

    implements(IAutoTOC)

    silvaconf.icon('www/autotoc.png')
    silvaconf.priority(0.2)

    def __init__(self, id):
        AutoTOC.inheritedAttribute('__init__')(self, id)
        #it'd be really nice if these could be placed in the Interface, and z3-ized
        self._local_types = ['Silva Document', 'Silva Publication',
                             'Silva Folder']
        self._toc_depth = -1
        self._display_desc_flag = False
        #possible values: 'silva', 'alpha', 'reversealpha', 'chronmod', 'rchronmod'
        self._sort_order = 'silva'
        self._show_icon = False

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
        if not hasattr(self, '_toc_depth'):
            self._toc_depth = -1
        return self._toc_depth

    security.declareProtected(SilvaPermissions.ReadSilvaContent, 'get_silva_types')
    def get_silva_types(self):
        st = self.get_silva_addables_allowed_in_container()
        return st

    security.declareProtected(SilvaPermissions.View, 'get_local_types')
    def get_local_types(self):
        if not hasattr(self, '_local_types'):
            self._local_types = ['Silva Document', 'Silva Publication',
                                 'Silva Folder']
        return self._local_types

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'set_local_types')
    def set_local_types(self, types):
        self._local_types = types

    security.declareProtected(SilvaPermissions.View, 'display_desc_flag')
    def display_desc_flag(self):
        if not hasattr(self,'_display_desc_flag'):
            self._display_desc_flag = False
        return self._display_desc_flag

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'set_display_desc_flag')
    def set_display_desc_flag(self, flag):
        self._display_desc_flag = not not flag

    security.declareProtected(SilvaPermissions.View, 'show_icon')
    def show_icon(self):
        if not hasattr(self,'_show_icon'):
            self._show_icon = False
        return self._show_icon

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'set_show_icon')
    def set_show_icon(self, flag):
        self._show_icon = not not flag

    security.declareProtected(SilvaPermissions.View, 'sort_order')
    def sort_order(self):
        if not hasattr(self, '_sort_order'):
            self._sort_order = 'silva'
        return self._sort_order

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'set_sort_order')
    def set_sort_order(self, order):
        self._sort_order = order


InitializeClass(AutoTOC)


class AutoTOCView(silvaviews.View):

    silvaconf.context(IAutoTOC)

    def render(self):
        # The following adapters should be merged with the current view.
        toc = self.context
        adapter = tocrendering.getTOCRenderingAdapter(toc)
        return adapter.render_tree(toc_depth=toc.toc_depth(),
                                   display_desc_flag=toc.display_desc_flag(),
                                   sort_order=toc.sort_order(),
                                   show_types=toc.get_local_types(),
                                   show_icon=toc.show_icon())


class AutoTOCPolicy(Persistent):

    implements(IContainerPolicy)

    def createDefaultDocument(self, container, title):
        container.manage_addProduct['Silva'].manage_addAutoTOC(
            'index', title)
        container.index.sec_update_last_author_info()

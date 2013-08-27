# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Persistence import Persistent

# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.interfaces import IAutoTOC, IContainerPolicy
from silva.translations import translate as _


class AutoTOC(Content, SimpleItem):
    __doc__ = _("""This is a special document type that automatically generates
    a Table of Contents. Usually it's used as the 'index' document of a folder.
    Then the parent folder displays a TOC when accessed (e.g.
    http://www.x.yz/silva/myFolder). The AutoTOC is configurable: it can display
    any selection of Silva content including assets, include descriptions or
    icons, be set to stop at a specific depth, and use various sorting
    methods.
    """)
    security = ClassSecurityInfo()

    meta_type = "Silva AutoTOC"

    grok.implements(IAutoTOC)
    silvaconf.icon('icons/autotoc.png')
    silvaconf.priority(0.2)

    _local_types = ['Silva Document', 'Silva Publication', 'Silva Folder']
    _toc_depth = -1
    _display_desc_flag = False
    # values: 'silva', 'alpha', 'reversealpha', 'chronmod', 'rchronmod'
    _sort_order = 'silva'
    _show_icon = False
    _show_container_link = False

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_toc_depth')
    def set_toc_depth(self, depth):
        self._toc_depth = depth

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_toc_depth')
    def get_toc_depth(self):
        """get the depth to which the toc will be rendered"""
        return self._toc_depth

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_show_container_link')
    def set_show_container_link(self, flag):
        self._show_container_link = flag

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_show_container_link')
    def get_show_container_link(self):
        """get the depth to which the toc will be rendered"""
        return self._show_container_link

    security.declareProtected(
        SilvaPermissions.View, 'get_local_types')
    def get_local_types(self):
        return self._local_types

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_local_types')
    def set_local_types(self, types):
        self._local_types = types

    security.declareProtected(SilvaPermissions.View, 'get_display_desc_flag')
    def get_display_desc_flag(self):
        return self._display_desc_flag

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_display_desc_flag')
    def set_display_desc_flag(self, flag):
        self._display_desc_flag = flag

    security.declareProtected(
        SilvaPermissions.View, 'get_show_icon')
    def get_show_icon(self):
        return self._show_icon

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_show_icon')
    def set_show_icon(self, flag):
        self._show_icon = flag

    security.declareProtected(
        SilvaPermissions.View, 'get_sort_order')
    def get_sort_order(self):
        return self._sort_order

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_sort_order')
    def set_sort_order(self, order):
        self._sort_order = order


InitializeClass(AutoTOC)


class AutoTOCPolicy(Persistent):
    grok.implements(IContainerPolicy)

    def createDefaultDocument(self, container, title):
        factory = container.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', title)

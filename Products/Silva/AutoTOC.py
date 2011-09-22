# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope import schema, interface
from zope.component import getUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Persistence import Persistent

# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions
from Products.Silva.adapters import tocrendering
from Products.SilvaMetadata.interfaces import IMetadataService

from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from silva.core.interfaces import IAutoTOC, IContainerPolicy
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from zeam.form import silva as silvaforms


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
    silvaconf.icon('www/autotoc.png')
    silvaconf.priority(0.2)

    _local_types = ['Silva Document', 'Silva Publication', 'Silva Folder', 
                    'Silva File']
    _toc_depth = -1
    _display_desc_flag = True
    # values: 'silva', 'alpha', 'reversealpha', 'chronmod', 'rchronmod'
    _sort_order = 'alpha'
    _show_icon = True
    _show_container_link = False

    # ACCESSORS
    security.declareProtected(
        SilvaPermissions.View, 'is_cacheable')
    def is_cacheable(self):
        """Return true if this document is cacheable.
        That means the document contains no dynamic elements like
        code, toc, etc.
        """
        return 0

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'can_set_title')
    def can_set_title(self):
        """always settable"""
        # XXX: we badly need Publishable type objects to behave right.
        return 1

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

@apply
def sort_order_source():
    orders = []
    for key, title in [
        ('silva', _(u'Silva folder order')),
        ('alpha', _(u'Alphabetically')),
        ('reversealpha', _(u'Reverse alphabetically')),
        ('chronmod', _(u'Chronologically by modification date')),
        ('rchronmod', _(u'Reverse chronologically by modification date'))]:
        orders.append(SimpleTerm(value=key, token=key, title=title))
    return SimpleVocabulary(orders)


@grok.provider(IContextSourceBinder)
def silva_content_types(context):
    contents = []
    for addable in context.get_silva_addables():
        contents.append(SimpleTerm(
                value=addable['name'],
                token=addable['name'],
                title=addable['name']))
    return SimpleVocabulary(contents)


class IAutoTOCSchema(interface.Interface):
    _local_types = schema.Set(
        title=_(u"types to list"),
        description=_(
            u"Select here the content types you wish to see in "
            u"the table of content. You need to selected container types "
            u"(e.g. Folder and Publication) in order for the TOC to "
            u"display their contents."),
        value_type=schema.Choice(source=silva_content_types),
        default=set(['Silva Document', 'Silva Folder', 'Silva Publication']),
        required=True)
    _toc_depth = schema.Int(
        title=_(u"depth"),
        description=_(
            u"The depth to which the Table of Contents will be rendered "
            u"(-1 means unlimited depth.)"),
        default=-1,
        min=-1,
        required=True)
    _display_desc_flag = schema.Bool(
        title=_(u"display description"),
        description=_(
            u"If selected, each item displayed will include its title "
            u"and metadata description, if available. "),
        default=False,
        required=True)
    _show_icon = schema.Bool(
        title=_("show icon"),
        description=_(
            u"If selected, each item displayed will include its icon. "),
        default=False,
        required=True)
    _show_container_link = schema.Bool(
        title=_("show container link"),
        description=_(
            u"If selected, there will be a link to the container "
            u"(as an H3) before the TOC list."),
        default=False,
        required=True)
    _sort_order = schema.Choice(
        title=_(u"sort order"),
        description=_(u"The order items in a container will be sorted"),
        source=sort_order_source,
        default='silva',
        required=True)


class AutoTOCAddForm(silvaforms.SMIAddForm):
    """Add an Auto TOC.
    """
    grok.context(IAutoTOC)
    grok.name(u'Silva AutoTOC')

    fields = silvaforms.Fields(ITitledContent, IAutoTOCSchema)


class AutoTOCEditForm(silvaforms.SMIEditForm):
    """Add an Auto TOC.
    """
    grok.context(IAutoTOC)

    fields = silvaforms.Fields(IAutoTOCSchema)


class AutoTOCView(silvaviews.View):
    grok.context(IAutoTOC)

    def update(self):
        renderer = tocrendering.getTOCRenderingAdapter(self.context)
        self.tree = renderer.render_tree(
            toc_depth=self.context.get_toc_depth(),
            display_desc_flag=self.context.get_display_desc_flag(),
            sort_order=self.context.get_sort_order(),
            show_types=self.context.get_local_types(),
            show_icon=self.context.get_show_icon())
        metadata = getUtility(IMetadataService)
        self.description = metadata.getMetadataValue(
            self.context, 'silva-extra', 'content_description', acquire=0)


class AutoTOCPolicy(Persistent):
    grok.implements(IContainerPolicy)

    def createDefaultDocument(self, container, title):
        factory = container.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', title)

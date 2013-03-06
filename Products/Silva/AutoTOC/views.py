# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok

from zope.component import getUtility
from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.SilvaMetadata.interfaces import IMetadataService

from silva.core.interfaces import IAutoTOC
from silva.core.views import views as silvaviews
from silva.core.conf.interfaces import ITitledContent
from silva.core.interfaces import IAddableContents, IPublishable
from silva.translations import translate as _
from zeam.form import silva as silvaforms


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
    container = context.get_container()
    addables = IAddableContents(container)
    for addable in addables.get_container_addables(IPublishable):
        contents.append(SimpleTerm(
                value=addable,
                token=addable,
                title=addable))
    return SimpleVocabulary(contents)


class IAutoTOCSchema(ITitledContent):
    _local_types = schema.Set(
        title=_(u"Types to list"),
        description=_(
            u"Select here the content types you wish to see in "
            u"the table of content. You need to selected container types "
            u"(e.g. Folder and Publication) in order for the TOC to "
            u"display their contents."),
        value_type=schema.Choice(source=silva_content_types),
        default=set(['Silva Document', 'Silva Folder', 'Silva Publication']),
        required=True)
    _toc_depth = schema.Int(
        title=_(u"Depth"),
        description=_(
            u"The depth to which the Table of Contents will be rendered "
            u"(-1 means unlimited depth.)"),
        default=-1,
        min=-1,
        max=99,
        required=True)
    _display_desc_flag = schema.Bool(
        title=_(u"Display description"),
        description=_(
            u"If selected, each item displayed will include its title "
            u"and metadata description, if available. "),
        default=False,
        required=True)
    _show_icon = schema.Bool(
        title=_("Show icon"),
        description=_(
            u"If selected, each item displayed will include its icon. "),
        default=False,
        required=True)
    _show_container_link = schema.Bool(
        title=_("Show container link"),
        description=_(
            u"If selected, there will be a link to the container "
            u"(as an H3) before the TOC list."),
        default=False,
        required=True)
    _sort_order = schema.Choice(
        title=_(u"Sort order"),
        description=_(u"The order items in a container will be sorted"),
        source=sort_order_source,
        default='silva',
        required=True)


@silvaforms.customize(name='_toc_depth', schema=IAutoTOCSchema)
def customize_toc_depth(field):
    field.htmlAttributes['style'] = 'width: 4em;'


class AutoTOCAddForm(silvaforms.SMIAddForm):
    """Add an Auto TOC.
    """
    grok.context(IAutoTOC)
    grok.name(u'Silva AutoTOC')

    fields = silvaforms.Fields(IAutoTOCSchema)


class AutoTOCEditForm(silvaforms.SMIEditForm):
    """Add an Auto TOC.
    """
    grok.context(IAutoTOC)

    fields = silvaforms.Fields(IAutoTOCSchema).omit('id')


class AutoTOCView(silvaviews.View):
    grok.context(IAutoTOC)

    def update(self):
        metadata = getUtility(IMetadataService)
        self.description = metadata.getMetadataValue(
            self.context, 'silva-extra', 'content_description', acquire=0)

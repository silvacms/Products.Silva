# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from xml.sax.saxutils import escape

from Products.Silva.icon import get_icon_url

from five import grok
from silva.core.interfaces import ISilvaObject, IContainer, IPublishable
from silva.core.interfaces import IAddableContents, IOrderManager
from silva.core.views.interfaces import IPreviewLayer
from silva.core.views import views as silvaviews
from zope.traversing.browser import absoluteURL
from zope.contentprovider.interfaces import ITALNamespaceData
from zope.interface import Interface, directlyProvides
from zope import schema


class ITOCRenderingOptions(Interface):
    toc_container = schema.Object(
        title=u'Container to render', schema=IContainer)
    toc_depth = schema.Int(
        title=u'TOC depth')
    toc_sort_order = schema.TextLine(
        title=u'TOC sorting order')
    toc_content_types = schema.List(
        title=u'TOC content type to show', value_type=schema.TextLine())
    toc_show_description = schema.Bool(
        title=u"Show content description")
    toc_show_icon = schema.Bool(
        title=u"Show content icon")

directlyProvides(ITOCRenderingOptions, ITALNamespaceData)


class TOCRendering(silvaviews.ContentProvider):
    """Render a toc.
    """
    grok.name('toc')
    grok.context(ISilvaObject)
    grok.implements(ITOCRenderingOptions)

    def __init__(self, *args):
        super(TOCRendering, self).__init__(*args)
        self.toc_container = None
        self.toc_depth = -1
        self.toc_sort_order = 'silva'
        self.toc_content_types = None
        self.toc_show_description = False
        self.toc_show_icon = False

    def update(self):
        if self.toc_container is None:
            self.toc_container = self.context.get_container()
        if self.toc_content_types is None:
            addables = IAddableContents(self.toc_container)
            self.toc_content_types = addables.get_container_addables(IPublishable)

    def list_container_items(self, container, is_displayable):
        """List the given container items that are a candidates to be
        listed in the TOC.
        """
        reverse_sort = self.toc_sort_order.startswith('r')
        items = filter(
            is_displayable,
            container.objectValues(self.toc_content_types))
        if self.toc_sort_order in ('alpha','reversealpha'):
            items.sort(
                key=lambda o: o.get_title_or_id(),
                reverse=reverse_sort)
        elif self.toc_sort_order in ('silva', 'reversesilva'):
            # determine silva sorting.
            # we should only have publishable content
            items.sort(
                key=IOrderManager(container).get_position,
                reverse=reverse_sort)
        else:
            # chronologically by modification date
            items.sort(
                key=lambda o: o.get_modification_datetime(),
                reverse=reverse_sort)
        return items

    def is_preview_displayable(self, item):
        """Return true if the item is displayable in preview mode.
        """
        return IPublishable.providedBy(item) and not item.is_default()

    def is_public_displayable(self, item):
        """Return true if the item is displayable in public mode.
        """
        return (IPublishable.providedBy(item) and
                (not item.is_default()) and
                item.is_published())

    def list_toc_items(self, container, level, is_displayable):
        """Yield for every element in this toc.  The 'depth' argument
        limits the number of levels, defaults to unlimited.
        """
        toc_filter = self.context.service_toc_filter
        can_recurse = self.toc_depth == -1 or level < self.toc_depth

        for item in self.list_container_items(
            container, is_displayable):

            if toc_filter.filter(item):
                    continue
            yield (level, item)

            if IContainer.providedBy(item) and can_recurse:
                for data in self.list_toc_items(item, level + 1, is_displayable):
                    yield data

    def render(self):
        public = not IPreviewLayer.providedBy(self.request)

        # XXX This code should be made readable.
        is_displayable = public and self.is_public_displayable or self.is_preview_displayable
        html = []
        a_templ = '<a href="%s">%s</a>'

        depth = -1
        prev_depth = [-1]
        gmv = self.context.service_metadata.getMetadataValue
        item = None
        for (depth, item) in self.list_toc_items(self.toc_container, 0, is_displayable):
            pd = prev_depth[-1]
            if pd < depth: #down one level
                html.append('<ul class="toc">')
                prev_depth.append(depth)
            elif pd > depth: #up one level
                for i in range(pd-depth):
                    prev_depth.pop()
                    html.append('</ul></li>')
            elif pd == depth: #same level
                html.append('</li>')
            html.append('<li>')
            if self.toc_show_icon:
                html.append('<img src="%s" />' % get_icon_url(item , self.request))
            title = (public and item.get_title() or item.get_title_editable()) or item.id
            html.append(a_templ % (absoluteURL(item, self.request), escape(title)))
            if self.toc_show_description:
                v = public and item.get_viewable() or item.get_previewable()
                desc = v and gmv(v,'silva-extra','content_description', acquire=0)
                if desc:
                    html.append('<p>%s</p>'%desc)
        else:
            #do this when the loop is finished, to
            #ensure that the lists are ended properly
            #the last item in the list could part of a nested list (with depth 1,2,3+, etc)
            #so need to loop down the depth and close all open lists
            while depth >= 0:
                html.append('</li></ul>')
                depth -= 1
        return u'\n'.join(html)

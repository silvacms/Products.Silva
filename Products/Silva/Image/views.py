# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt


from five import grok
from zope.component import getMultiAdapter
from zope.interface import Interface

from silva.core.views import views as silvaviews
from silva.core.views.traverser import SilvaPublishTraverse
from silva.core.interfaces import IImage


class DefaultImageView(silvaviews.View):
    """View a Image in the SMI / preview. For this just return a
    tag.

    Note that if you ask directly the URL of the image, you will
    get it, not this view (See the traverser below).
    """
    grok.context(IImage)
    grok.require('zope2.View')

    def render(self):
        return self.content.tag()


class ImagePublishTraverse(SilvaPublishTraverse):

    def browserDefault(self, request):
        # We don't want to lookup five views if we have other than a
        # GET or HEAD request, but delegate to the sub-object.
        content, method = super(ImagePublishTraverse, self).browserDefault(
            request)
        if request.method in ('GET', 'HEAD',):
            query = request.QUERY_STRING
            if query == 'hires':
                img = self.context.hires_image
            elif query == 'thumbnail':
                img = self.context.thumbnail_image
            else:
                img = self.context.image
            view = getMultiAdapter((img, request), Interface, name='index.html')
            view.__parent__ = img
            method = {'GET': tuple(), 'HEAD': ('HEAD',)}.get(request.method)
            return (view, method)
        return content, method

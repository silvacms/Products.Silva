# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt


from five import grok
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.datetime import time as time_from_datetime

from silva.core.views import views as silvaviews
from silva.core.views.traverser import SilvaPublishTraverse
from silva.core.views.httpheaders import HTTPResponseHeaders
from silva.core.interfaces import IImage

from Products.Silva.File.views import FileResponseHeaders, FDIterator



class DefaultImageView(silvaviews.View):
    """View a Image in the SMI / preview. For this just return a
    tag.

    Note that if you ask directly the URL of the image, you will
    get it, not this view (See the traverser below).
    """
    grok.context(IImage)
    grok.require('zope2.View')

    hires = False
    thumbnail = False

    def render(self):
        return self.content.tag(request=self.request,
                                hires=self.hires,
                                preview=self.is_preview,
                                thumbnail=self.thumbnail)


class ImageResponseHeaders(HTTPResponseHeaders):
    grok.adapts(IBrowserRequest, IImage)

    def other_headers(self, headers):
        query = self.request.QUERY_STRING
        if query == 'hires':
            img = self.context.hires_image
        elif query == 'thumbnail':
            img = self.context.thumbnail_image
        else:
            img = self.context.image
        FileResponseHeaders(self.request, img).other_headers(headers)


class ImageDownloadView(silvaviews.View):
    grok.context(IImage)
    grok.require('zope2.View')
    grok.name('index.html')

    hires = False
    thumbnail = False

    def update(self):
        query = self.request.QUERY_STRING
        if query == 'hires':
            self.img = self.context.hires_image
        elif query == 'thumbnail':
            self.img = self.context.thumbnail_image
        else:
            self.img = self.context.image

    def render(self):
        header = self.request.environ.get('HTTP_IF_MODIFIED_SINCE', None)
        if header is not None:
            header = header.split(';')[0]
            try:
                mod_since = long(time_from_datetime(header))
            except:
                mod_since = None
            if mod_since is not None:
                last_mod = self.context.get_modification_datetime()
                if last_mod is not None:
                    last_mod = long(last_mod)
                    if last_mod > 0 and last_mod <= mod_since:
                        self.response.setStatus(304)
                        return u''
        return FDIterator(self.img.get_file_fd())


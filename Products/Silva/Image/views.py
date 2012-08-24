# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import getMultiAdapter

from webdav.common import rfc1123_date

from Products.Silva.File.views import FileDownloadView
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders
from silva.core.interfaces import IImage


class ImageView(silvaviews.View):
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


class ImageDownloadView(FileDownloadView):
    grok.context(IImage)

    def payload(self):
        query = self.request.QUERY_STRING
        if query == 'hires':
            img = self.context.hires_image
        elif query == 'thumbnail':
            img = self.context.thumbnail_image
        else:
            img = self.context.image

        view = getMultiAdapter((img, self.request), name='index.html')
        return view.payload()


class ImageResponseHeaders(HTTPResponseHeaders):
    """This reliably set HTTP headers on file serving, for GET and
    HEAD requests.
    """
    grok.adapts(IBrowserRequest, IImage)

    def other_headers(self, headers):
        image = self.context
        query = self.request.QUERY_STRING
        if query == 'hires':
            asset = image.hires_image
        elif query == 'thumbnail':
            asset = image.thumbnail_image
        else:
            asset = image.image

        self.response.setHeader(
            'Content-Disposition',
            'inline;filename=%s' % (asset.get_filename()))
        self.response.setHeader(
            'Content-Type',
            asset.get_content_type())
        if asset.get_content_encoding():
            self.response.setHeader(
                'Content-Encoding',
                asset.get_content_encoding())
        self.response.setHeader(
            'Content-Length',
            asset.get_file_size())
        self.response.setHeader(
            'Last-Modified',
            rfc1123_date(image.get_modification_datetime()))
        self.response.setHeader(
            'Accept-Ranges',
            'none')


# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import getMultiAdapter

from webdav.common import rfc1123_date
from zExceptions import NotFound

from Products.Silva.File.views import FileDownloadView
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders
from silva.core.interfaces import IImage, IHTTPHeadersSettings


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
        return self.content.get_html_tag(
            request=self.request,
            hires=self.hires,
            preview=self.is_preview,
            thumbnail=self.thumbnail)


class ImageDownloadView(FileDownloadView):
    grok.context(IImage)

    def payload(self):
        query = self.request.QUERY_STRING
        image = None
        if query == 'hires':
            image = self.context.hires_image
        elif query == 'thumbnail':
            image = self.context.thumbnail_image
        if image is None:
            image = self.context.image

        if image is None:
            raise NotFound('Image resolution unavailable')
        view = getMultiAdapter((image, self.request), name='index.html')
        return view.payload()


class HTTPHeadersSettings(grok.Annotation):
    """Settings used to manage regular headers on Silva content.
    """
    grok.provides(IHTTPHeadersSettings)
    grok.context(IImage)
    grok.implements(IHTTPHeadersSettings)

    http_disable_cache = False
    http_max_age = 86400
    http_last_modified = True


class ImageResponseHeaders(HTTPResponseHeaders):
    """This reliably set HTTP headers on file serving, for GET and
    HEAD requests.
    """
    grok.adapts(IBrowserRequest, IImage)

    def other_headers(self, headers):
        image = self.context
        query = self.request.QUERY_STRING
        asset = None
        if query == 'hires':
            asset = image.hires_image
        elif query == 'thumbnail':
            asset = image.thumbnail_image
        if asset is None:
            asset = image.image

        if self._include_last_modified:
            self.response.setHeader(
                'Last-Modified',
                rfc1123_date(image.get_modification_datetime()))
        if asset is None:
            # No asset, just return.
            return
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
        if not self.response.getHeader('Content-Length'):
            self.response.setHeader(
                'Content-Length',
                asset.get_file_size())
        if not self.response.getHeader('Accept-Ranges'):
            self.response.setHeader(
                'Accept-Ranges',
                'none')


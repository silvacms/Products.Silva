# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from zope.component import getMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest

# Zope 2
from AccessControl import getSecurityManager
from AccessControl import Unauthorized

# Silva
from silva.core.interfaces import IGhostAsset, IDownloableAsset
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders
from silva.core.views.interfaces import IHTTPResponseHeaders
from silva.translations import translate as _


class GhostAssetView(silvaviews.View):
    grok.context(IGhostAsset)
    grok.require('zope2.View')

    def render(self):
        haunted = self.context.get_haunted()
        if haunted is None:
            return _(u"This content is unavailable. "
                     u"Please inform the site manager.")
        permission = self.is_preview and 'Read Silva content' or 'View'
        if not getSecurityManager().checkPermission(permission, haunted):
            raise Unauthorized(
                u"You do not have permission to "
                u"see the target of this ghost")
        if IDownloableAsset.providedBy(haunted):
            return haunted.get_html_tag(
                request=self.request, preview=self.is_preview)
        return _(u"This content cannot be previewed.")


class GhostAssetDownloadView(silvaviews.View):
    grok.context(IGhostAsset)
    grok.require('zope2.View')
    grok.name('index.html')

    def render(self):
        haunted = self.context.get_haunted()
        if haunted is None:
            self.response.setStatus(404)
            return u''
        permission = self.is_preview and 'Read Silva content' or 'View'
        if not getSecurityManager().checkPermission(permission, haunted):
            raise Unauthorized(
                u"You do not have permission to "
                u"see the target of this ghost")
        view = getMultiAdapter((haunted, self.request), name='index.html')
        return view()


class GhostAssetResponseHeaders(HTTPResponseHeaders):
    """This reliably set HTTP headers on file serving, for GET and
    HEAD requests.
    """
    grok.adapts(IBrowserRequest, IGhostAsset)

    def other_headers(self, headers):
        haunted = self.context.get_haunted()
        if haunted is not None:
            headers = getMultiAdapter(
                (self.request, haunted),
                IHTTPResponseHeaders)
            headers.other_headers(headers)


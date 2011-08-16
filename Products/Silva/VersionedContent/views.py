# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
import lxml.html.diff

from silva.core.views import views as silvaviews
from silva.core.interfaces import IVersion, IVersionedContent
from silva.translations import translate as _
from silva.core.views.interfaces import IPreviewLayer


class CompareVersion(silvaviews.Page):
    grok.context(IVersionedContent)
    grok.name('compare_versions.html')
    grok.require('silva.ReadSilvaContent')

    def update(self):
        self.version1 = None
        self.version2 = None
        self.version1_id = self.request.form.get('version1')
        self.version2_id = self.request.form.get('version2')
        if self.version1_id is not None:
            content = self.context._getOb(self.version1_id, None)
            if IVersion.providedBy(content):
                self.version1 = content
        if self.version2_id is not None:
            content = self.context._getOb(self.version2_id, None)
            if IVersion.providedBy(content):
                self.version2 = content

    def render(self):
        if self.version1 is None or self.version2 is None:
            return _(u"Missing or invalid version identifier")

        alsoProvides(self.request, IPreviewLayer)

        version1_view = getMultiAdapter(
            (self.context, self.request), name='content.html')
        version1_view.content = self.version1
        version1_html = version1_view()

        version2_view = getMultiAdapter(
            (self.context, self.request), name='content.html')
        version2_view.content = self.version2
        version2_html = version2_view()

        return lxml.html.diff.htmldiff(version2_html, version1_html)

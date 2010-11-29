# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from silva.core.interfaces import ISilvaObject


class RenderExternalSource(grok.View):
    grok.context(ISilvaObject)
    grok.name('render_extsource')
    grok.require('silva.ChangeSilvaContent')

    def render(self):
        parameters = self.request.form.copy()
        source_id = parameters.get("source_id", "")
        docref = parameters.get("docref", "")
        if source_id  and docref:
            source = getattr(self.context, source_id, None)
            if source is None:
                return u""
            if source.is_previewable():
                del parameters['source_id']
                del parameters['docref']
                version = getUtility(IIntIds).getObject(int(docref))
                return source.to_html(
                    version, self.request, **parameters)
        return u""

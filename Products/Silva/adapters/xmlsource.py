# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.publisher.interfaces.browser import IBrowserRequest
from Products.Silva.silvaxml import xmlexport
from silva.core.interfaces import IXMLSource, ISilvaObject, IVersion


class XMLSourceAdapter(grok.MultiAdapter):
    """Adapter for Silva objects to get their XML content.
    """
    grok.implements(IXMLSource)
    grok.provides(IXMLSource)
    grok.adapts(ISilvaObject, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_XML(self, version=xmlexport.PREVIEWABLE_VERSION, options={}):
        settings = xmlexport.ExportSettings(request=self.request,
                                            options=options)
        settings.setVersion(version)
        settings.setExternalRendering(True)

        xml, info = xmlexport.exportToString(self.context, settings)
        return xml


class XMLSourceVersionAdapter(XMLSourceAdapter):
    """XMLSourceAdapter for content version.
    """
    grok.adapts(IVersion, IBrowserRequest)



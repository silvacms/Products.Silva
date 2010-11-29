# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core import interfaces
from zope.publisher.interfaces.browser import IBrowserRequest

from Products.Silva.silvaxml import xmlexport
from Products.Silva.transform.interfaces import IXMLSource


class XMLSourceAdapter(grok.MultiAdapter):
    """Adapter for Silva objects to get their XML content.
    """
    grok.implements(IXMLSource)
    grok.provides(IXMLSource)
    grok.adapts(interfaces.ISilvaObject, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getXML(self, version=xmlexport.PREVIEWABLE_VERSION, options={}):
        settings = xmlexport.ExportSettings(request=self.request,
                                            options=options)
        settings.setVersion(version)
        settings.setExternalRendering(True)

        xml, info = xmlexport.exportToString(self.context, settings)
        return xml


class XMLSourceVersionAdapter(XMLSourceAdapter):
    """XMLSourceAdapter for content version.
    """
    grok.adapts(interfaces.IVersion, IBrowserRequest)



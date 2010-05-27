# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.core import interfaces
from Products.Silva.silvaxml import xmlexport
from Products.Silva.transform.interfaces import IXMLSource


class XMLSourceAdapter(grok.Adapter):
    """Adapter for Silva objects to get their XML content.
    """
    grok.implements(IXMLSource)
    grok.provides(IXMLSource)
    grok.context(interfaces.ISilvaObject)

    def getXML(self,
               version=xmlexport.PREVIEWABLE_VERSION,
               external_rendering=False):
        # Set settings
        settings = xmlexport.ExportSettings()
        settings.setVersion(version)
        settings.setExternalRendering(external_rendering)

        xml, info = xmlexport.exportToString(self.context, settings)
        return xml


class XMLSourceVersionAdapter(XMLSourceAdapter):
    """XMLSourceAdapter for content version.
    """
    grok.context(interfaces.IVersion)



# Copyright (c) 2002-2009 Infrae. All rights reserved.
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
    grok.context(interfaces.ISilvaObject)

    def getXML(self, 
               version=xmlexport.PREVIEWABLE_VERSION,
               external_rendering=False):
        # Set settings
        settings = xmlexport.ExportSettings()
        settings.setVersion(version)
        settings.setExternalRendering(external_rendering)

        # Export to string
        info = xmlexport.ExportInfo()
        exporter = xmlexport.theXMLExporter
        exportRoot = xmlexport.SilvaExportRoot(self.context)
        return exporter.exportToString(exportRoot, settings, info)

    
class XMLSourceVersionAdapter(XMLSourceAdapter):
    """XMLSourceAdapter for content version.
    """

    grok.context(interfaces.IVersion)



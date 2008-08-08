# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from grokcore import component

from Products.Silva import interfaces as silva_interfaces
from Products.Silva.silvaxml import xmlexport
from Products.Silva.transform.interfaces import IXMLSource

class XMLSourceAdapter(component.Adapter):
    """Adapter for Silva objects to get their XML content.
    """

    component.implements(IXMLSource)
    component.context(silva_interfaces.ISilvaObject)

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

    component.context(silva_interfaces.IVersion)


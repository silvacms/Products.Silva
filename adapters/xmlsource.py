from zope.interface import implements
import Globals
from Products.Silva.silvaxml import xmlexport
from Products.Silva.adapters import adapter
from Products.Silva.transform.interfaces import IXMLSource

class XMLSourceAdapter(adapter.Adapter):
    """Adapter for Silva objects to get their XML content."""

    implements(IXMLSource)

    def getXML(self, **kwargs):
        settings = xmlexport.ExportSettings(**kwargs)
        settings.setExternalRendering(True)
        info = xmlexport.ExportInfo()
        exporter = xmlexport.theXMLExporter
        exportRoot = xmlexport.SilvaExportRoot(self.context)
        return exporter.exportToString(exportRoot, settings, info)

Globals.InitializeClass(XMLSourceAdapter)

def getXMLSourceAdapter(context):
    return XMLSourceAdapter(context).__of__(context)
    

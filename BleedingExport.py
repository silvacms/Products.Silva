from Products.Silva.silvaxml import xmlexport

def bleeding_export(self):
    xmlexport.initializeXMLExportRegistry()
    settings = xmlexport.ExportSettings()
    exporter = xmlexport.theXMLExporter
    xml_source = xmlexport.SilvaExportRoot(self.Test_OOo_Publication)
    export_soup = exporter.exportToString(xml_source, settings)
    export_bowl = open("/Users/bradb/Desktop/Test_OOo_Publication.slv", "w")
    export_bowl.write(export_soup)

    return ''

from Products.Silva.silvaxml import xmlexport

def bleeding_export(self):
    xmlexport.initializeXMLSourceRegistry()
    settings = xmlexport.ExportSettings()
    xml_source = xmlexport.getXMLSource(self.Test_OOo_Publication)
    export_soup = xml_source.xmlToString(settings)
    export_bowl = open("/Users/bradb/Desktop/Test_OOo_Publication.slv", "w")
    export_bowl.write(export_soup)

    return ''

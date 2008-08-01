from tempfile import TemporaryFile

# Zope 3
from zope.interface import implements
from zope.component import adapts

# Zope 2
import Globals
from AccessControl import ClassSecurityInfo

# Silva
from Products.Silva.adapters import adapter, interfaces
from Products.Silva import interfaces as silva_interfaces
from Products.Silva import SilvaPermissions


class ZipfileExportAdapter(adapter.Adapter):
    """ Adapter for silva objects to facilitate
    the export to zipfiles. 
    """

    implements(interfaces.IDefaultContentExporter)
    adapts(silva_interfaces.ISilvaObject)
    
    security = ClassSecurityInfo()

    name = "Full Media (zip)"
    extension = "zip"

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'export')    
    def export(self, settings=None):
        from zipfile import ZipFile, ZIP_DEFLATED
        from Products.Silva.silvaxml import xmlexport
        tempFile = TemporaryFile()
        archive = ZipFile(tempFile, "wb", ZIP_DEFLATED)

        # export context to xml and add xml to zip
        if settings == None:
            settings = xmlexport.ExportSettings()
        exporter = xmlexport.theXMLExporter
        info = xmlexport.ExportInfo()
        exportRoot = xmlexport.SilvaExportRoot(self.context)

        archive.writestr(
            'silva.xml', 
            exporter.exportToString(exportRoot, settings, info)
            )
        
        # process data from the export, i.e. export binaries
        for path, id in info.getAssetPaths():
            asset = self.context.restrictedTraverse(path)
            # XXX Code will change when AssetData adapters are phased out
            adapter = interfaces.IAssetData(asset)
            if adapter is not None:
                asset_path = 'assets/%s' % id
                archive.writestr(
                    asset_path,
                    adapter.getData())
        for path, id in info.getZexpPaths():
            ob = self.context.restrictedTraverse(path)
            obid = ob.id
            if callable(obid):
                obid = obid()
            archive.writestr(
                'zexps/' + id,
                ob.aq_parent.manage_exportObject(
                    obid,
                    download=True))
        archive.close()
        tempFile.seek(0)
        value = tempFile.read()
        tempFile.close()
        return value
    
        
Globals.InitializeClass(ZipfileExportAdapter)

    

# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from tempfile import TemporaryFile

from five import grok

from Products.Silva import interfaces as interfaces


class ZipFileExportAdapter(grok.Adapter):
    """ Adapter for silva objects to facilitate
    the export to zipfiles.
    """

    grok.implements(interfaces.IDefaultContentExporter)
    grok.context(interfaces.ISilvaObject)
    grok.name('zip')

    name = "Full Media (zip)"
    extension = "zip"

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






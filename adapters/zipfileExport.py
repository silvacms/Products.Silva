# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from tempfile import TemporaryFile
from zipfile import ZipFile, ZIP_DEFLATED

from five import grok

from silva.core import interfaces

from Products.Silva.silvaxml import xmlexport


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
        tempFile = TemporaryFile()
        archive = ZipFile(tempFile, "w", ZIP_DEFLATED)

        # export context to xml and add xml to zip
        xml, info = xmlexport.exportToString(self.context, settings)

        archive.writestr('silva.xml', xml)

        # process data from the export, i.e. export binaries
        for path, id in info.getAssetPaths():
            asset = self.context.restrictedTraverse(path)
            adapter = interfaces.IAssetData(asset)
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






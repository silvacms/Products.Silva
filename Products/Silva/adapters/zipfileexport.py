# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from cStringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED

from five import grok
from zope.interface import Interface
from zope import schema

from silva.core import interfaces
from silva.translations import translate as _

import transaction

from Products.Silva.silvaxml import xmlexport


class IExportOptions(Interface):
    include_sub_publications = schema.Bool(
        title=_(u"Include sub publications?"),
        description=_(u"Check to export all sub publications. "),
        default=False,
        required=False)

    export_newest_version_only = schema.Bool(
        title=_(u"Export only newest versions?"),
        description=_(u"If not checked all versions are exported."),
        default=True,
        required=False)


class ZipFileExportAdapter(grok.Adapter):
    """ Adapter for silva objects to facilitate
    the export to zipfiles.
    """
    grok.implements(interfaces.IDefaultContentExporter)
    grok.provides(interfaces.IContentExporter)
    grok.context(interfaces.ISilvaObject)
    grok.name('zip')

    name = "Full Media (zip)"
    extension = "zip"
    options = IExportOptions

    def export(self, **options):
        settings = xmlexport.ExportSettings()
        settings.setWithSubPublications(
            options['include_sub_publications'])
        settings.setLastVersion(
            options['export_newest_version_only'])

        archive_file = StringIO()
        archive = ZipFile(archive_file, "w", ZIP_DEFLATED)

        # export context to xml and add xml to zip
        xml, info = xmlexport.exportToString(self.context, settings)
        archive.writestr('silva.xml', xml)

        # process data from the export, i.e. export binaries
        for path, id in info.getAssetPaths():
            asset = self.context.restrictedTraverse(path)
            adapter = interfaces.IAssetData(asset)
            archive.writestr('assets/' + id, adapter.getData())

        unknowns = info.getZexpPaths()
        if unknowns:
            # This is required is exported content have been created
            # in the same transaction than the export. They need to be
            # in the database in order to be exported.
            transaction.savepoint()
            for path, id in unknowns:
                export = StringIO()
                content = self.context.restrictedTraverse(path)
                content._p_jar.exportFile(content._p_oid, export)
                archive.writestr('zexps/' + id, export.getvalue())
                export.close()

        archive.close()
        return archive_file.getvalue()






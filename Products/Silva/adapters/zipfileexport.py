# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import io
from zipfile import ZipFile, ZIP_DEFLATED

from five import grok
from zope.interface import Interface
from zope import schema

from silva.core import interfaces
from silva.core.xml import Exporter
from silva.translations import translate as _

import transaction


class IExportOptions(Interface):
    publications = schema.Bool(
        title=_(u"Include sub publications?"),
        description=_(u"Check to export all sub publications. "),
        default=False,
        required=False)
    others = schema.Bool(
        title=_(u"Include other contents?"),
        description=_(u"Check to export content not providing an XML "
                      u"export functionality. This can cause problems."),
        default=True,
        required=False)
    previewable = schema.Bool(
        title=_(u"Export only newest versions?"),
        description=_(u"If not checked all versions are exported."),
        default=True,
        required=False)
    references = schema.Bool(
        title=_(u'Export content refering non-exported one?'),
        description=_(u"If checked, export content refering "
                      u"not exported one without error."),
        default=False,
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

    def export(self, request, stream=None, in_memory=False, **options):
        if stream is None:
            stream = io.BytesIO()
            in_memory = True
        archive = ZipFile(stream, "w", ZIP_DEFLATED)

        exporter = Exporter(self.context, request, options)
        # Export context to xml and add xml to zip
        export = exporter.getStream()
        archive.write(export.filename, 'silva.xml')
        export.close()

        # process data from the export, i.e. export binaries
        for path, id in exporter.getAssetPaths():
            asset = self.context.restrictedTraverse(path)
            adapter = interfaces.IAssetData(asset)
            archive.writestr('assets/' + id, adapter.getData())

        unknowns = exporter.getZexpPaths()
        if unknowns:
            # This is required is exported content have been created
            # in the same transaction than the export. They need to be
            # in the database in order to be exported.
            transaction.savepoint()
            for path, id in unknowns:
                export = io.BytesIO()
                content = self.context.restrictedTraverse(path)
                content._p_jar.exportFile(content._p_oid, export)
                archive.writestr('zexps/' + id, export.getvalue())
                export.close()

        archive.close()
        if in_memory:
            return stream.getvalue()
        return stream






# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zipfile import ZipFile

from five import grok
from silva.core.interfaces import IZipFileImporter, IContainer
from silva.core.xml import ZipImporter


class ZipFileImporter(grok.Adapter):
    """ Adapter for silva objects to facilitate
    the full media import from zipfiles.
    """
    grok.implements(IZipFileImporter)
    grok.provides(IZipFileImporter)
    grok.context(IContainer)

    def isFullmediaArchive(self, input_archive):
        """Returns true if the archive is a fullmedia archive
        """
        archive = ZipFile(input_archive, 'r')
        try:
            if 'silva.xml' in archive.namelist():
                return True
            return False
        finally:
            archive.close()

    def importFromZip(self, input_archive, request, options={}):
        """ imports fullmedia zipfile
        """
        importer = ZipImporter(self.context, request, options)
        importer.importStream(input_archive)
        return importer

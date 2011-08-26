# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zipfile import ZipFile
from cStringIO import StringIO

from five import grok

# Silva
from Products.Silva.silvaxml import xmlimport

from silva.core.interfaces import IZipFileImporter, IContainer


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

    def importFromZip(self, input_archive, request, replace=0):
        """ imports fullmedia zipfile
        """
        existing_objects = self.context.objectIds()

        archive = ZipFile(input_archive, 'r')
        source_file = StringIO(archive.read('silva.xml'))
        try:
            imported = xmlimport.importFromFile(
                source_file, self.context, request,
                zip_file=archive, replace=replace)

            succeeded = []
            failed = []
            for id in imported.objectIds():
                if id not in existing_objects:
                    succeeded.append(id)
            return succeeded, failed
        finally:
            source_file.close()
            archive.close()


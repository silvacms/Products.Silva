# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zipfile import ZipFile

from five import grok

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva.silvaxml import xmlimport
from Products.Silva import SilvaPermissions

from silva.core.interfaces import IZipFileImporter, IContainer


class ZipFileImportAdapter(grok.Adapter):
    """ Adapter for silva objects to facilitate
    the full media import from zipfiles.
    """
    grok.implements(IZipFileImporter)
    grok.provides(IZipFileImporter)
    grok.context(IContainer)

    security = ClassSecurityInfo()
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'isFullmediaArchive')
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

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'importFromZip')
    def importFromZip(self, input_archive, replace=0):
        """ imports fullmedia zipfile
        """
        existing_objects = self.context.objectIds()

        archive = ZipFile(input_archive, 'r')
        info = xmlimport.ImportInfo()
        info.setZIPFile(archive)
        source_file = info.getFileFromZIP('silva.xml')
        try:
            imported = xmlimport.importFromFile(
                source_file, self.context, info=info, replace=replace)

            succeeded = []
            failed = []
            for id in imported.objectIds():
                if id not in existing_objects:
                    succeeded.append(id)
            return succeeded, failed
        finally:
            source_file.close()
            archive.close()


InitializeClass(ZipFileImportAdapter)


def __allow_access_to_unprotected_subobjects__(name,value=None):
    return name in ('getZipfileImportAdapter')


def getZipfileImportAdapter(context):
    adapter = IZipFileImporter(context, None)
    if adapter is not None:
        # For ZODB-script security
        adapter.__parent__ = context
    return adapter

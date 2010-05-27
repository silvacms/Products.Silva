# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from StringIO import StringIO
from zipfile import ZipFile

from five import grok

# Zope
from AccessControl import ClassSecurityInfo, allow_module
from App.class_init import InitializeClass

# Silva
from silva.core.interfaces import IZipfileImporter, IContainer

# Silva Adapters
from Products.Silva.silvaxml import xmlimport
from Products.Silva import SilvaPermissions


class ZipfileImportAdapter(grok.Adapter):
    """ Adapter for silva objects to facilitate
    the full media import from zipfiles.
    """

    grok.implements(IZipfileImporter)
    grok.provides(IZipfileImporter)
    grok.context(IContainer)

    security = ClassSecurityInfo()
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'isFullmediaArchive')
    def isFullmediaArchive(self, archive):
        """Returns true if the archive is a fullmedia archive
        """
        archive = ZipFile(archive, 'r')
        try:
            if 'silva.xml' in archive.namelist():
                return True
            return False
        finally:
            archive.close()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'importFromZip')
    def importFromZip(self, container, zipfile, replace=0):
        """ imports fullmedia zipfile
        """
        # XXX container should be self.context !@!#?#?!!!
        existing_objects = container.objectIds()
        archive = ZipFile(zipfile, 'r')
        info = xmlimport.ImportInfo()
        info.setZipFile(archive)
        source_file = StringIO(archive.read('silva.xml'))
        if replace:
            result = xmlimport.importReplaceFromFile(
                source_file,
                container,
                info=info)
        else:
            result = xmlimport.importFromFile(
                source_file,
                container,
                info=info)
        source_file.close()
        archive.close()

        succeeded = []
        failed = []
        for id in result.objectIds():
            if id not in existing_objects:
               succeeded.append(id)
        return succeeded, failed

InitializeClass(ZipfileImportAdapter)

allow_module('Products.Silva.adapters.zipfileimport')

__allow_access_to_unprotected_subobjects__ = True

def getZipfileImportAdapter(context):
    adapter = IZipfileImporter(context, None)
    if adapter is not None:
        # For ZODB-script security
        adapter.__parent__ = context
    return adapter

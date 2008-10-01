# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: archivefileimport.py,v 1.7 2006/01/24 16:12:01 faassen Exp $
#
# Python
import os.path
import zipfile
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
    
from zope.interface import implements
# Zope
import Globals
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo, allow_module
from zope import contenttype
# Silva
from Products.Silva import interfaces
from Products.Silva import SilvaPermissions
from Products.Silva import mangle
from Products.Silva import assetregistry
# Catch all asset for files of unknown mimetypes
from Products.Silva import File
# Silva Adapters
from Products.Silva.adapters import adapter

BadZipfile = zipfile.BadZipfile

class ArchiveFileImportAdapter(adapter.Adapter):
    """ Adapter for container-like objects to facilitate
    the import of archive files (e.g. zipfiles) and create
    Assets out of its contents and, optionally, to recreate
    the 'directory' structure contained in the archive file.
    """

    implements(interfaces.IArchiveFileImporter, )
    
    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'importArchive')    
    def importArchive(self, archive, assettitle='', recreatedirs=1, replace=0):
        zip = zipfile.ZipFile(archive)
        
        # Lists the names of the files in the archive which were succesfully 
        # added (or, if something went wrong, list it in failed_list).
        succeeded_list = []
        failed_list = []
        
        # Extract filenames, not directories.
        for name in zip.namelist():
            extracted_file = StringIO(zip.read(name))
            mimetype, enc = contenttype.guess_content_type(name)
            path, filename = os.path.split(name)
            if not filename:
                # Its a directory entry
                continue
            
            if recreatedirs and path:
                dirs = path.split('/')
                container = self._getSilvaContainer(
                    self.context, dirs, replace)
                if container is None:
                    failed_list.append('/'.join(dirs))
                    # Creating the folder failed - bailout for this
                    # zipped file...
                    continue
            else:
                filename = name
                container = self.context
                
            # Actually add object...
            factory = self._getFactoryForMimeType(mimetype)

            id = self._makeId(filename, container, extracted_file, replace)
            added_object = factory(
                container, id, assettitle, extracted_file)
            if added_object is None:
                # Factories return None upon failure.
                # FIXME: can I extract some info for the reason of failure?
                failed_list.append(name)
            else:
                added_object.sec_update_last_author_info()
                succeeded_list.append(name)

        return succeeded_list, failed_list
    
    def _makeId(self, filename, container, extracted_file, replace):
        if replace:
            id = filename
            if id in container.objectIds():
                container.manage_delObjects([id])
        else:
            id = self._getUniqueId(
                container, filename, file=extracted_file, 
                interface=interfaces.IAsset)
        return id
    
    def _getSilvaContainer(self, context, path, replace=0):
        container = context
        for id in path:
            if replace and id in container.objectIds():
                container = getattr(container, id)
            else:
                container = self._addSilvaContainer(container, id)
        return container
    
    def _addSilvaContainer(self, context, id):
        IContainer = interfaces.IContainer
        
        idObj = mangle.Id(context, id, interface=IContainer, allow_dup=1)
        if not idObj.isValid():
            return None
        
        while id in context.objectIds():
            obj = context[id]
            if IContainer.providedBy(obj):
                return obj
            id = str(idObj.new())
        context.manage_addProduct['Silva'].manage_addFolder(id, id)
        return context[id]
    
    def _getUniqueId(self, context, suggestion, **kw):
        # Make filename valid and unique.
        id = mangle.Id(context, suggestion, **kw)
        id.cook().unique()
        return str(id)
    
    def _getFactoryForMimeType(self, mimetype):
        root = self.context.get_root()
        factory = assetregistry.getFactoryForMimetype(root, mimetype)
        if factory is None:
            return File.manage_addFile
        return factory
    
Globals.InitializeClass(ArchiveFileImportAdapter)

allow_module('Products.Silva.adapters.archivefileimport')

__allow_access_to_unprotected_subobjects__ = True
    
module_security = ModuleSecurityInfo('Products.Silva.adapters.archivefileimport')
    
module_security.declareProtected(
    SilvaPermissions.ChangeSilvaContent, 'getArchiveFileImportAdapter')
def getArchiveFileImportAdapter(context):
    if not interfaces.IContainer.providedBy(context):
        # raise some exception here?
        return None
    return ArchiveFileImportAdapter(context).__of__(context)

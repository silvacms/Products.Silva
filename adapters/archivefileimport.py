# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: archivefileimport.py,v 1.6 2005/11/14 18:06:13 faassen Exp $
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
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
from OFS import content_types
# Silva
from Products.Silva import interfaces as silva_interfaces
from Products.Silva import SilvaPermissions
from Products.Silva import mangle
from Products.Silva import assetregistry
# Catch all asset for files of unknown mimetypes
from Products.Silva import File
# Silva Adapters
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces

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
    def importArchive(self, archive, assettitle='', recreatedirs=1):
        zip = zipfile.ZipFile(archive)
        
        # Lists the names of the files in the archive which were succesfully 
        # added (or, if something went wrong, list it in failed_list).
        succeeded_list = []
        failed_list = []
        
        # Extract filenames, not directories.
        for name in zip.namelist():
            extracted_file = StringIO(zip.read(name))
            mimetype, enc = content_types.guess_content_type(name)
            path, filename = os.path.split(name)
            if not filename:
                # Its a directory entry
                continue
            
            if recreatedirs and path:
                dirs = path.split('/')
                container = self._getSilvaContainer(self.context, dirs)
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
            
            id = self._getUniqueId(
                container, filename, file=extracted_file, 
                interface=silva_interfaces.IAsset)
            
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
    
    def _getSilvaContainer(self, context, path):
        container = context
        for id in path:
            container = self._addSilvaContainer(container, id)
        return container
    
    def _addSilvaContainer(self, context, id):
        IContainer = silva_interfaces.IContainer
        
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

def getArchiveFileImportAdapter(context):
    if not silva_interfaces.IContainer.providedBy(context):
        # raise some exception here?
        return None
    return ArchiveFileImportAdapter(context).__of__(context)

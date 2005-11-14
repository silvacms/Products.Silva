from StringIO import StringIO
from zope.interface import implements

# Zope
import Globals
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
# Silva
from Products.Silva import interfaces as silva_interfaces
# Silva Adapters
from Products.Silva.adapters import adapter, interfaces, assetdata
from Products.Silva.adapters import interfaces
from Products.Silva import SilvaPermissions

class ZipfileImportAdapter(adapter.Adapter):
    """ Adapter for silva objects to facilitate
    the full media import from zipfiles. 
    """

    implements(interfaces.IZipfileImporter)
    
    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'isFullmediaArchive')    
    def isFullmediaArchive(self, archive):
        """Returns true if the archive is a fullmedia archive
        """
        from zipfile import ZipFile
        archive = ZipFile(archive, 'r')
        # XXX: this is very simplistic. 
        # TODO: Fullmedia archives should have a manifest file.
        if 'silva.xml' in archive.namelist():
            return True 
        return False 

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'importFromZip')    
    def importFromZip(self, container, zipfile):
        """ imports fullmedia zipfile 
        """
        from zipfile import ZipFile
        from Products.Silva.silvaxml import xmlimport

        existing_objects = container.objectIds()
        archive = ZipFile(zipfile, 'r')
        info = xmlimport.ImportInfo()
        info.setZipFile(archive)
        source_file = StringIO(archive.read('silva.xml'))
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
        
Globals.InitializeClass(ZipfileImportAdapter)

def getZipfileImportAdapter(context):
    if not silva_interfaces.IContainer.providedBy(context):
        # raise some exception here?
        return None

    return ZipfileImportAdapter(context).__of__(context)

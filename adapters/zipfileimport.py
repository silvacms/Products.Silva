from StringIO import StringIO
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

    __implements__ = (interfaces.IZipfileImporter, )
    
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

        importer = xmlimport.theXMLImporter
        archive = ZipFile(zipfile, 'r')
        settings = xmlimport.ImportSettings()
        info = xmlimport.ImportInfo()
        info.setZipFile(archive)
        bytes = archive.read('silva.xml')
        source_file = StringIO(bytes)
        importer.importFromFile(
            source_file,
            result=container,
            settings=settings,
            info=info)
        source_file.close()
        archive.close()

        succeeded = []
        failed = []
        return succeeded, failed
        
Globals.InitializeClass(ZipfileImportAdapter)

def getZipfileImportAdapter(context):
    if not silva_interfaces.IContainer.isImplementedBy(context):
        # raise some exception here?
        return None

    return ZipfileImportAdapter(context).__of__(context)

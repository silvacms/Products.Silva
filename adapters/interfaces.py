from Interface import Interface

class IViewerSecurity(Interface):
    def setAcquired():
        """Set minimum viewer role restriction to acquire from above.
        """
        
    def setMinimumRole(role):
        """Set the minimum (viewer) role needed for view permission here.

        If role is Anonymous, viewer role restriction will be set to
        acquire from above.
        """

    def isAcquired():
        """Check whether minimum role is acquired.
        """
        
    def getMinimumRole():
        """Get the minimum role needed for view permission here.
        """

    def getMinimumRoleAbove():
        """Get the minimum role needed for view permission in parent.
        """

class ILockable(Interface):
    def createLock():
        """Create lock for context object.

        Return false if already locked, otherwise true.
        """

    def breakLock():
        """Break the lock.
        """

    def isLocked():
        """Check whether this object is locked by another user.
        """

class IArchiveFileImporter(Interface):
    def importArchive(archivefile, assettitle=None, recreatedirs=1):
        """Import archive file
        
        Use 'assettitle' for the title to set on all assets created
        
        According to the recreatedirs setting, create a substructure of
        Silva Containers (probably Silva Folders) reflecting the structure
        of the archive file. This substructure will be created relative to
        the adapted context.
        
        Return a tuple with the list of succeeded items and failed items
        providing feedback on what archive contents have succesfully been 
        imported into Silva Assets and what contents have not.
        """

class IZipfileExporter(Interface):
    def exportToZip(context, zipname, settings):
        """Export Silva content to a zip file.
        
        context -- The content object to be exported
        zipname -- The filename of the zip archive
        settings -- The export settings
        """

class IAssetData(Interface):
    def getData():
        """ Get actual data stored for this asset as calling index_html()
        for assets can have all kinds of unwanted side effects.
        """        
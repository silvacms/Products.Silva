from zope.interface import Interface

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
    def importArchive(archivefile, assettitle=None, recreatedirs=1, replace=0):
        """Import archive file
        
        Use 'assettitle' for the title to set on all assets created
        
        According to the recreatedirs setting, create a substructure of
        Silva Containers (probably Silva Folders) reflecting the structure
        of the archive file. This substructure will be created relative to
        the adapted context.
        
        If replace is true, replace items with identical ids.
        
        Return a tuple with the list of succeeded items and failed items
        providing feedback on what archive contents have succesfully been 
        imported into Silva Assets and what contents have not.
        """

class IZipfileImporter(Interface):
    def isFullmediaArchive(zipname):
        """Tests if the zip archive is a fullmedia archive
        """

    def importFromZip(context, zipname, replace=False):
        """Import Silva content from a full media zip file.

        context -- The content object to be imported into
        zipname -- The filename of the zip archive
        replace -- Replace content objects with identical ids.
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

class IVersionManagement(Interface):
    def getVersionById(id):
        """get a version by id"""

    def getPublishedVersion():
        """return the current published version, None if it doesn't exist"""

    def getUnapprovedVersion():
        """return the current unapproved (editable) version, None if it doesn't exist"""

    def getApprovedVersion():
        """return the current approved version, None if it doesn't exist"""

    def revertPreviousToEditable(id):
        """revert a previous version to be editable version

            The current editable will become the last closed (last closed
            will move to closed list). If the published version will not be
            changed.
            
            Raises AttributeError when version id is not available.
            
            Raises VersioningError when 'editable' version is approved or
            in pending for approval.
        """

    def getVersionIds():
        """return a list of all version ids"""

    def getVersions(sort_attribute='id'):
        """return a list of version objects
        
            if sort_attribute resolves to False, no sorting is done,
            by default it sorts on id converted to int (so [0,1,2,3,...]
            instead of [0,1,10,2,3,...] if values < 20)
        """

    def deleteVersion(id):
        """delete a version

            can raise AttributeError when the version doesn't exist, 
            VersioningError if the version is approved(XXX?) or published
        """

    def deleteOldVersions(number_to_keep):
        """delete all but <number_to_keep> last closed versions

            can be called only by managers, and should be used with great care,
            since it can potentially remove interesting versions
        """
    
class IAddables(Interface):

    def getAddables():
        """return a list of Metatypes that are addable to this container."""
        
    def setAddables(addables):
        """set the the Metatypes that are addable to this container."""
            
class IIndexable(Interface):
    def getTitle():
        """returns the title of the indexable."""

    def getPath():
        """returns the path of the indexable."""

    def getIndexes():
        """returns the indexes for a certain object, or an empty list."""

class ILanguageProvider(Interface):
    def getAvailableLanguages():
        """return the available languages"""

    def setPreferredLanguage(language):
        """sets the preferred language"""

    def getPreferredLanguage():
        """gets the preferred language"""

class IPath(Interface):
    def pathToUrl(path):
        """convert a physical path to a URL"""

    def urlToPath(url):
        """convert a HTTP URL to a physical path"""

class ICatalogIndexable(Interface):
    """Index and reindex an object.
    """
    def index():
        """Index an object.
        """

    def unindex():
        """Unindex an object.
        """
        
    def reindex():
        """Reindex an object.
        """
class IFeed(Interface):
    """
    Atom or RSS2 feed
    """
    def getFeed(format='atom'):
        """Get the atom or rss2 feed for a container like Silva object. 
        """
        
class IFeedItem(Interface):
    """
    Atom or RSS2 feed item
    """
    def getFeedItem(format='atom'):
        """Get the atom or rss2 feed item representation for a Silva object. 
        """

# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

"""This module contains interfaces declarations for adapters used in Silva.
"""

from zope.interface import Interface, Attribute

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


class IContentImporter(Interface):
    """Generic content importer.
    """


class IArchiveFileImporter(IContentImporter):
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


class IZipfileImporter(IContentImporter):
    def isFullmediaArchive(zipname):
        """Tests if the zip archive is a fullmedia archive
        """

    def importFromZip(context, zipname, replace=False):
        """Import Silva content from a full media zip file.

        context -- The content object to be imported into
        zipname -- The filename of the zip archive
        replace -- Replace content objects with identical ids.
        """


class IContentExporter(Interface):
    """Adapter for export context content in a file.
    """

    name = Attribute("Name of the registered exporter")
    extension = Attribute("Filename extension for this exporter")

    def export(settings):
        """Export context with given settings.
        """


class IDefaultContentExporter(IContentExporter):
    """This mark the default content exporter.
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
        """return the current unapproved (editable) version, None if
        it doesn't exist"""

    def getApprovedVersion():
        """return the current approved version, None if it doesn't exist"""

    def revertPreviousToEditable(id):
        """revert a previous version to be editable version

        The current editable will become the last closed (last closed
        will move to closed list). If the published version will not
        be changed.

        Raises AttributeError when version id is not available.

        Raises VersioningError when 'editable' version is approved or
        in pending for approval.
        """

    def getVersionIds():
        """return a list of all version ids
        """

    def getVersions(sort_attribute='id'):
        """return a list of version objects

        If sort_attribute resolves to False, no sorting is done, by
        default it sorts on id converted to int (so [0,1,2,3,...]
        instead of [0,1,10,2,3,...] if values < 20).
        """

    def deleteVersion(id):
        """Delete a version

        Can raise AttributeError when the version doesn't exist,
        VersioningError if the version is approved(XXX?) or published.
        """

    def deleteOldVersions(number_to_keep):
        """Delete all but <number_to_keep> last closed versions.

        Can be called only by managers, and should be used with great care,
        since it can potentially remove interesting versions
        """


class IAddables(Interface):

    def getAddables():
        """Return a list of Metatypes that are addable to this container.
        """

    def setAddables(addables):
        """Set the the Metatypes that are addable to this container.
        """


class IIndexable(Interface):

    def getTitle():
        """Returns the title of the indexable.
        """

    def getPath():
        """Returns the path of the indexable.
        """

    def getIndexes():
        """Returns the indexes for a certain object, or an empty list.
        """


class ILanguageProvider(Interface):

    def getAvailableLanguages():
        """Return the available languages.
        """

    def setPreferredLanguage(language):
        """Sets the preferred language.
        """

    def getPreferredLanguage():
        """Gets the preferred language.
        """

class IPath(Interface):

    def pathToUrl(path):
        """Convert a physical path to a URL.
        """

    def urlToPath(url):
        """Convert a HTTP URL to a physical path.
        """


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


class IFeedEntry(Interface):
    """Interface for objects that can act like an item in a atom or rss
    feed.
    """

    def id():
        pass

    def title():
        pass

    def html_description():
        pass

    def description():
        pass

    def url():
        pass

    def authors():
        pass

    def date_updated():
        pass

    def date_published():
        pass

    def keywords():
        pass


class IVirtualHosting(Interface):
    """Access to virtual hosting information.
    """

    def getVirtualRootPhysicalPath():
        """ Get the physical path of the object being the virtual host
        root.

        If there is no virtual hosting, return None
        """

    def getVirtualHostKey():
        """ Get a key for the virtual host root.

        If there is no virtual hosting, return None.
        """

    def getVirtualRoot():
        """ Get the virtual host root object.
        """

    def getSilvaOrVirtualRoot():
        """ Get either the virtual host root object, or the silva root.
        """

    def containsVirtualRoot():
        """ Return true if object contains the current virtual host root.
        """


class ISubscribable(Interface):
    """Subscribable interface
    """

    def isSubscribable():
        """Return True if the adapted object is actually subscribable,
        False otherwise.
        """
        pass

    def subscribability():
        """
        """
        pass

    def getSubscribedEmailaddresses():
        """
        """
        pass

    def getSubscriptions():
        """Return a list of ISubscription objects
        """
        pass

    def isValidSubscription(emailaddress, token):
        """Return True is the specified emailaddress and token depict a
        valid subscription request. False otherwise.
        """
        pass

    def isValidCancellation(emailaddress, token):
        """Return True is the specified emailaddress and token depict a
        valid cancellation request. False otherwise.
        """
        pass

    def isSubscribed(emailaddress):
        """Return True is the specified emailaddress is already subscribed
        for the adapted object. False otherwise.
        """
        pass

    def setSubscribable(bool):
        """Set the subscribability to True or False for the adapted object.
        """
        pass

    def subscribe(emailaddress):
        """Subscribe emailaddress for adapted object.
        """
        pass

    def unsubscribe(emailaddress):
        """Unsubscribe emailaddress for adapted object.
        """
        pass

    def generateConfirmationToken(emailaddress):
        """Generate a token used for the subscription/cancellation cycle.
        """
        pass


class ISiteManager(Interface):
    """Site Manager adapter.
    """

    def makeSite():
        """Make the context become a local site.
        """

    def unmakeSite():
        """Release the context of being a local site.
        """

    def isSite():
        """Return true if the context is a local site.
        """


class IHaunted(Interface):
    """Interface for haunted adapter
    """

    def getHaunting():
        """Return iterator of objects (ghosts) haunting the adapted object.
        """
        pass

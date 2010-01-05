# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os

# Zope 3
from zope.app.component.hooks import setSite
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.container.interfaces import IObjectMovedEvent
from five import grok

# Zope 2
from OFS.interfaces import IObjectWillBeAddedEvent
from OFS.interfaces import IObjectWillBeMovedEvent
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
try:
    from App.class_init import InitializeClass # Zope 2.12
except ImportError:
    from Globals import InitializeClass # Zope < 2.12

from DateTime import DateTime
import transaction

# Silva
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.Publication import Publication
from Products.Silva.helpers import add_and_edit
from Products.Silva import SilvaPermissions
from Products.Silva import install

from silva.core.services import site
from silva.core.interfaces import IRoot
from silva.core import conf as silvaconf


icon="www/silva.png"


class DocumentationInstallationException(Exception):
    """Raised when a dependency is not installed when trying to
    install something.
    """


class SilvaGlobals(grok.DirectoryResource):
    # This export the globals directory using Zope 3 technology.
    grok.path('globals')
    grok.name('silva.globals')


class Root(Publication, site.Site):
    """Root of Silva site.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Root"

    # We do not want to register Root automaticaly.
    grok.implements(IRoot)
    silvaconf.icon('www/silva.png')
    silvaconf.factory('manage_addRootForm')
    silvaconf.factory('manage_addRoot')

    def __init__(self, id):
        super(Root, self).__init__(id)
        # if we add a new root, version starts out as the software version
        self._content_version = self.get_silva_software_version()

    # MANIPULATORS

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_folder')
    def to_folder(self):
        """Don't do anything here. Can't do this with root.
        """
        pass

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'add_silva_addable_forbidden')
    def add_silva_addable_forbidden(self, meta_type):
        """Add a meta_type that is forbidden from use in this site.
        """
        addables_forbidden = getattr(self.aq_base, '_addables_forbidden', {})
        addables_forbidden[meta_type] = 0
        self._addables_forbidden = addables_forbidden

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'clear_silva_addables_forbidden')
    def clear_silva_addables_forbidden(self):
        """Clear out all forbidden addables; everything allowed now.
        """
        self._addables_forbidden = {}

    # ACCESSORS
    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'serviceIds')
    def serviceIds(self):
        """Show all service ids.
        """
        return [id for id in Root.inheritedAttribute('objectIds')(self)
                if id.startswith('service_')]


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_root')
    def get_root(self):
        """Get root of site. Can be used with acquisition get the
        'nearest' Silva root.
        """
        return self.aq_inner

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_root_url')
    def get_root_url(self):
        """Get url of root of site.
        """
        return self.aq_inner.absolute_url()

    def get_other_content(self):
        """Gets non-asset, non-publishable content.

        Overrides the implementation in Folder to not return Silva internal
        files.
        """
        return ()

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_silva_addables_allowed_in_container')
    def get_silva_addables_allowed_in_container(self):
        # allow everything in silva by default, unless things are restricted
        # explicitly
        if not hasattr(self,'_addables_allowed_in_container'):
            self._addables_allowed_in_container = None
        addables = self._addables_allowed_in_container
        if addables is None:
            return self.get_silva_addables_all()
        else:
            return addables

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_silva_addable_forbidden')
    def is_silva_addable_forbidden(self, meta_type):
        """Return true if addable is forbidden to be used in this
        site.
        """
        if not hasattr(self.aq_base, '_addables_forbidden'):
            return 0
        else:
            return self._addables_forbidden.has_key(meta_type)

    security.declarePublic('get_silva_software_version')
    def get_silva_software_version(self):
        """The version of the Silva software.
        """
        return extensionRegistry.get_extension('Silva').version

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_silva_content_version')
    def get_silva_content_version(self):
        """Return the version of Silva content.

        This version is usually the same as the software version, but
        can be different in case the content was not yet updated.
        """
        return getattr(self, '_content_version', 'before 0.9.2')

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'upgrade_silva')
    def upgrade_silva(self):
        """Upgrade Silva from previous version.

            returns nothing
            an exception is raised on error
        """
        from_version = self.get_silva_content_version()
        to_version = self.get_silva_software_version()
        from silva.core.upgrade import upgrade
        upgrade.registry.upgrade(self, from_version, to_version)
        self._content_version = to_version

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                                'upgrade_silva_object')
    def upgrade_silva_object(self, from_version, object_path):
        """EXPERIMENTAL partial upgrade functionality

            upgrades a single object (recursively) in the Silva tree
            rather than the whole Silva root, can be used to upgrade
            imported content
        """
        object = self.restrictedTraverse(object_path)
        to_version = self.get_silva_software_version()
        from silva.core.upgrade import upgrade
        upgrade.registry.upgrade(object, from_version, to_version)

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'status_update')
    def status_update(self):
        """Updates status for objects that need status updated

        Searches the ZCatalog for objects that should be published or closed
        and updates the status accordingly
        """
        if not getattr(self, 'service_catalog', None):
            return 'No catalog found!'

        # first get all approved objects that should be published
        query = {'silva-extrapublicationtime': DateTime(),
                 'silva-extrapublicationtime_usage': 'range:max',
                 'version_status': 'approved'
                }

        result = self.service_catalog(query)

        # now get all published objects that should be closed
        query = {'silva-extraexpirationtime': DateTime(),
                 'silva-extraexpirationtime_usage': 'range:max',
                 'version_status': 'public'
                }

        result += self.service_catalog(query)

        for item in result:
            ob = item.getObject()
            ob.object()._update_publication_status()

        return 'Status updated'

    security.declarePublic('recordError')
    def recordError(self, message_type, message):
        """record given error/feedback

            actual logging is not implemented, just an idea; what really
            happens is a ZODB transaction rollback if message_type == 'error'

            message_type: either 'feedback' or 'error'
            message: string containing user readable error
            returns None
        """
        if message_type == 'error':
            transaction.abort()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_real_container')
    def get_real_container(self):
        """Get the container, even if we're a container.

        If we're the root object, returns None.

        Can be used with acquisition to get the 'nearest' container.
        """
        return None

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'manage_installDocumentation')
    def manage_installDocumentation(self):
        """Install user docs into the root, called from service_extensions"""
        self._installDocumentation()

    def _installDocumentation(self):
        """Install user documentation into the root"""
        try:
            import Products.SilvaDocument
        except ImportError:
            raise DocumentationInstallationException, 'Documentation can not be installed since SilvaDocument is not available'
        from adapters.zipfileimport import getZipfileImportAdapter
        importer = getZipfileImportAdapter(self)
        zipfile = open('%s/doc/silva_docs.zip' % os.path.dirname(__file__), 'rb')
        importer.importFromZip(self, zipfile)
        zipfile.close()

    def _installSilvaFindInstance(self):
        """Install a SilvaFind instance in the siteroot"""

        self.manage_addProduct['SilvaFind'
                               ].manage_addSilvaFind('search',
                                                     'Search this site')
        self.search.sec_update_last_author_info()


InitializeClass(Root)

manage_addRootForm = PageTemplateFile("www/rootAdd", globals(),
                                      __name__='manage_addRootForm')

def manage_addRoot(self, id, title, add_docs=0, add_search=0, REQUEST=None):
    """Add a Silva root."""
    # no id check possible or necessary, as this only happens rarely and the
    # Zope id check is fine
    root = Root(id)
    self._setObject(id, root)
    root = getattr(self, id)
    # transform title from whatever encoding it is in to unicode
    # we're assuming latin1 encoding. I guess this is not necessarily
    # correct in case the ZMI has been set to another encoding, but of course
    # it being Zope 2 there's no proper method on RESPONSE to get to this
    # information, and applying a regex to the content-type header seems
    # excessive
    title = unicode(title, 'latin1')
    # now set it all up
    setSite(root)
    install.installFromScratch(root)
    root.set_title(title)

    if add_search:
        # install a silva find instance
        root._installSilvaFindInstance()

    if add_docs:
        # install the user documentation .zexp
        root._installDocumentation()

    add_and_edit(self, id, REQUEST)
    return ''

@silvaconf.subscribe(IRoot, IObjectMovedEvent)
def root_moved(root, event):
    if not IObjectRemovedEvent.providedBy(event):
        root.index_object()

@silvaconf.subscribe(IRoot, IObjectWillBeMovedEvent)
def root_will_be_moved(root, event):
    if not IObjectWillBeAddedEvent.providedBy(event):
        root.unindex_object()

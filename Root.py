# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os

# Zope 3
from zope.interface import implements

# Zope 2
from OFS.interfaces import IObjectWillBeAddedEvent
from OFS.interfaces import IObjectWillBeMovedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.container.interfaces import IObjectMovedEvent
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass, DTMLFile
from DateTime import DateTime
import transaction

# Silva
from Products.Silva.Publication import Publication
from Products.Silva.helpers import add_and_edit
from Products.Silva.interfaces import IRoot, IInvisibleService
from Products.Silva import SilvaPermissions
from Products.Silva import install

from silva.core import conf


icon="www/silva.png"

class DocumentationInstallationException(Exception):
    """Raised when a dependency is not installed when trying to install something"""

class Root(Publication):
    """Root of Silva site.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Root"

    implements(IRoot)

    inherited_manage_options = Publication.manage_options
    manage_options= (
        (inherited_manage_options[0],) + # ({'label':'Contents', 'action':'manage_contents'},) +
        ({'label':'Services', 'action':'manage_services'},) +
        inherited_manage_options[1:]
        )

    conf.baseclass()

    def __init__(self, id):
        Root.inheritedAttribute('__init__')(self, id)
        # if we add a new root, version starts out as the software version
        self._content_version = self.get_silva_software_version()

    # MANIPULATORS

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'manage_main')
    manage_main = DTMLFile(
        'www/folderContents', globals())

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'manage_services')
    manage_services = DTMLFile(
        'www/folderServices', globals())

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

    security.declarePublic('objectItemsContents')
    def objectItemsContents(self, spec=None):
        """Don't display services by default in the Silva root.
        """
        return [item for item in Root.inheritedAttribute('objectItems')(self)
                if not item[0].startswith('service_')]

    security.declarePublic('objectItemsServices')
    def objectItemsServices(self, spec=None):
        """Display services separately.
        """
        return [item for item in Root.inheritedAttribute('objectItems')(self)
                if item[0].startswith('service_')
                and not IInvisibleService.providedBy(item[1])]

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
                              'get_silva_addables_allowed_in_publication')
    def get_silva_addables_allowed_in_publication(self):
        # allow everything in silva by default, unless things are restricted
        # explicitly
        addables = self._addables_allowed_in_publication
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

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_silva_software_version')
    def get_silva_software_version(self):
        """The version of the Silva software.
        """
        return '2.1'

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_silva_content_version')
    def get_silva_content_version(self):
        """Return the version of Silva content.

        This version is usually the same as the software version, but
        can be different in case the content was not yet updated.
        """
        return getattr(self, '_content_version', 'before 0.9.2')

    security.declarePublic('get_silva_product_version')
    def get_silva_product_version(self):
        """Returns the release version of the Product"""
        return self.manage_addProduct['Silva'].version

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'upgrade_silva')
    def upgrade_silva(self):
        """Upgrade Silva from previous version.

            returns nothing
            an exception is raised on error
        """
        from_version = self.get_silva_content_version()
        to_version = self.get_silva_software_version()
        from Products.Silva import upgrade
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
        from Products.Silva import upgrade
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
        message = 'Documentation installed'
        try:
            self._installDocumentation()
        except DocumentationInstallationException, e:
            message = e
        return self.service_extensions.manage_main(manage_tabs_message=message)

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
    object = Root(id)
    self._setObject(id, object)
    object = getattr(self, id)
    # transform title from whatever encoding it is in to unicode
    # we're assuming latin1 encoding. I guess this is not necessarily
    # correct in case the ZMI has been set to another encoding, but of course
    # it being Zope 2 there's no proper method on RESPONSE to get to this
    # information, and applying a regex to the content-type header seems
    # excessive
    title = unicode(title, 'latin1')
    # now set it all up
    install.installFromScratch(object)
    object.set_title(title)

    if add_search:
        # install a silva find instance
        object._installSilvaFindInstance()
        
    if add_docs:
        # install the user documentation .zexp
        object._installDocumentation()

    add_and_edit(self, id, REQUEST)
    return ''

@conf.subscribe(IRoot, IObjectMovedEvent)
def root_moved(root, event):
    if not IObjectRemovedEvent.providedBy(event):
        root.index_object()

@conf.subscribe(IRoot, IObjectWillBeMovedEvent)
def root_will_be_moved(root, event):
    if not IObjectWillBeAddedEvent.providedBy(event):
        root.unindex_object()

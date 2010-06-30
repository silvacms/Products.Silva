# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.site.hooks import setSite, setHooks
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Silva
from Products.Silva.ExtensionService import install_documentation
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.Publication import Publication
from Products.Silva.helpers import add_and_edit
from Products.Silva import SilvaPermissions
from Products.Silva import install

from silva.core.services import site
from silva.core.interfaces import IRoot
from silva.core import conf as silvaconf


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
    silvaconf.zmiAddable(True)
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
                              'status_update')
    def status_update(self):
        """Updates status for objects that need status updated

        Searches the ZCatalog for objects that should be published or closed
        and updates the status accordingly
        """
        if not getattr(self, 'service_catalog', None):
            return 'No catalog found!'

        # first get all approved objects that should be published
        query = {'silva-extrapublicationtime':
                     {'query': DateTime(), 'range': 'max'},
                 'version_status': 'approved'}

        result = self.service_catalog(query)

        # now get all published objects that should be closed
        query = {'silva-extraexpirationtime':
                     {'query': DateTime(), 'range': 'max'},
                 'version_status': 'public'}

        result += self.service_catalog(query)

        for item in result:
            ob = item.getObject()
            ob.get_content()._update_publication_status()

        return 'Status updated'

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_real_container')
    def get_real_container(self):
        """Get the container, even if we're a container.

        If we're the root object, returns None.

        Can be used with acquisition to get the 'nearest' container.
        """
        return None


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
    # this root is the new local site
    setSite(root)
    setHooks()
    # now set it all up
    install.installFromScratch(root)
    root.set_title(title)

    if add_search:
        # install a silva find instance
        factory = root .manage_addProduct['SilvaFind']
        factory.manage_addSilvaFind('search', 'Search this site')

    if add_docs:
        # install the user documentation .zexp
        install_documentation(root)

    add_and_edit(self, id, REQUEST)
    return ''


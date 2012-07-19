# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from five.localsitemanager import make_site
from zope import schema, interface, component
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.site.hooks import setSite, setHooks
from zope.traversing.browser import absoluteURL

# Zope 2
from AccessControl import ClassSecurityInfo, getSecurityManager
from App.class_init import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Application import Application
from zExceptions import Unauthorized
import Globals
import transaction

# Silva
from Products.Silva.ExtensionService import install_documentation
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.Publication import Publication
from Products.Silva.helpers import add_and_edit
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.conf import schema as silvaschema
from silva.core.interfaces import IRoot, ContentError
from silva.core.interfaces.events import InstallRootEvent
from silva.core.interfaces.events import InstallRootServicesEvent
from silva.core.messages.interfaces import IMessageService
from silva.translations import translate as _
from zeam.form import silva as silvaforms


class ISilvaRootAddFields(interface.Interface):
    """Describe an add form for a new Silva root.
    """
    identifier = silvaschema.ID(
        title=_(u"Site identifier"),
        required=True)
    title = schema.TextLine(
        title=_(u"Site title"),
        required=False)
    add_search = schema.Bool(
        title=_(u"Add search functionality?"),
        default=True,
        required=False)
    add_documentation = schema.Bool(
        title=_(u"Add user documentation?"),
        default=True,
        required=False)


class ZopeWelcomePage(silvaforms.ZMIForm):
    grok.context(Application)
    grok.name('index.html')

    fields = silvaforms.Fields(ISilvaRootAddFields)

    def update(self):
        self.sites = self.context.objectValues('Silva Root')
        self.is_dev = Globals.DevelopmentMode
        self.version = extensionRegistry.get_extension('Silva').version

    def is_allowed_to_add_root(self):
        return getSecurityManager().checkPermission(
            'View Management Screens', self.context)

    @silvaforms.action(
        _(u"Authenticate first to add a new site"),
        available=lambda form:not form.is_allowed_to_add_root())
    def login(self):
        if not self.is_allowed_to_add_root():
            raise Unauthorized("You must authenticate to add a new Silva Site")

    @silvaforms.action(
        _(u"Add a new site"),
        available=lambda form:form.is_allowed_to_add_root())
    def new_root(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        self.context.manage_addProduct['Silva'].manage_addRoot(
            data['identifier'],
            data.getDefault('title'))
        root = self.context._getOb(data['identifier'])
        service = component.getUtility(IMessageService)
        service.send(
            _(u"New Silva site ${identifier} added.",
              mapping={'identifier': data['identifier']}),
            self.request)

        if data.getDefault('add_search'):
            # install a silva find instance
            factory = root.manage_addProduct['SilvaFind']
            factory.manage_addSilvaFind('search', 'Search this site')

        if data.getDefault('add_documentation'):
            transaction.commit() # Be sure everything in the site is
                                 # in the DB before.  install the user
                                 # documentation .zexp
            install_documentation(root, self.request)

        self.redirect(absoluteURL(root, self.request) + '/edit')
        return silvaforms.SUCCESS


class Root(Publication):
    """Root of Silva site.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Root"

    # We do not want to register Root automaticaly.
    grok.implements(IRoot)
    silvaconf.icon('www/silva.png')
    silvaconf.zmi_addable(True)
    silvaconf.factory('manage_addRootForm')
    silvaconf.factory('manage_addRoot')

    _smi_skin = 'silva.ui.interfaces.ISilvaUITheme'
    _properties = Publication._properties + (
        {'id': '_smi_skin',
         'label': 'Skin SMI',
         'type': 'string',
         'mode': 'w'},)

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
        raise ContentError(
            _(u"Root cannot be converted to folder"), self)

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_publication')
    def to_publication(self):
        """Don't do anything here. Can't do this with root.
        """
        raise ContentError(
            _(u"Root cannot be converted to publication"), self)

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
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_root')
    def get_root(self):
        """Get root of site. Can be used with acquisition get the
        'nearest' Silva root.
        """
        return self.aq_inner

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

def manage_addRoot(self, id, title, REQUEST=None):
    """Add a Silva root.
    """
    if not title:
        title = id
    if not isinstance(title, unicode):
        title = unicode(title, 'latin1')
    id = str(id)
    container = self.Destination()

    # We suppress events are no local utility is present event
    # handlers all fails.
    root = Root(id)
    setattr(root, '__initialization__', True)
    container._setObject(id, root)
    root = container._getOb(id)
    # This root is the new local site where all local utilities (Silva
    # services) will be installed.
    make_site(root)
    setSite(root)
    setHooks()
    try:
        notify(InstallRootServicesEvent(root))
        notify(InstallRootEvent(root))

        root.set_title(title)
        delattr(root, '__initialization__')
        notify(ObjectCreatedEvent(root))

        if REQUEST is not None:
            add_and_edit(self, id, REQUEST)
    except:
        # If there is an error, reset the local site. This prevent
        # more confusion.
        setSite(None)
        setHooks()
        raise
    return root

# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from five.localsitemanager import make_site
from zope import schema, interface
from zope.event import notify
from zope.component import getUtility
from zope.lifecycleevent import ObjectCreatedEvent
from zope.site.hooks import setSite, setHooks
from zope.traversing.browser import absoluteURL

# Zope 2
from AccessControl import ClassSecurityInfo, getSecurityManager
from App.class_init import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Application import Application
from zExceptions import Unauthorized, Redirect
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
from silva.core.services.interfaces import IExtensionService, IMetadataService
from silva.translations import translate as _
from zeam.form import silva as silvaforms


class IQuotaRootManager(interface.Interface):
    """Describe a quota for a Silva root.
    """
    identifier = schema.TextLine(
        title=_(u"Site"),
        readonly=True,
        required=True)
    quota = schema.Int(
        title=_(u"Site quota"),
        min=-1,
        default=-1,
        required=True)
    used = schema.Float(
        title=_(u'Used space'),
        min=-1.0,
        readonly=True,
        required=True)


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
    grok.require('zope2.Public')

    fields = silvaforms.Fields(ISilvaRootAddFields)

    def update(self):
        self.sites = self.context.objectValues('Silva Root')
        self.is_dev = Globals.DevelopmentMode
        self.version = extensionRegistry.get_extension('Silva').version

    def is_manager(self):
        return getSecurityManager().checkPermission(
            'View Management Screens', self.context)

    @silvaforms.action(
        _(u"Authenticate first to add a new site"),
        identifier='login',
        available=lambda form:not form.is_manager())
    def login(self):
        if not self.is_manager():
            raise Unauthorized("You must authenticate to add a new Silva Site")

    @silvaforms.action(
        _(u"Add a new site"),
        identifier='add_site',
        available=lambda form:form.is_manager())
    def add_site(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        self.context.manage_addProduct['Silva'].manage_addRoot(
            data['identifier'],
            data.getDefault('title'))
        root = self.context._getOb(data['identifier'])
        getUtility(IMessageService).send(
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


class ManageSiteForm(silvaforms.ZMIComposedForm):
    grok.context(Application)
    grok.name('manage.html')


class QuotaRootFactory(object):

    def __init__(self, site):
        self._site = site
        self.identifier = site.getId()
        self.quota = -1
        self.used = -1
        quota = self._site.service_extensions.get_site_quota()
        if quota:
            self.quota = quota
        used = self._site.used_space
        if used:
            self.used = used / (1024*1014)

    def update(self, value):
        """Update the quota.
        """
        service = self._site.service_extensions
        if value > 0:
            service._site_quota = value
            if not service.get_quota_subsystem_status():
                try:
                    setSite(self._site)
                    setHooks()
                    service.enable_quota_subsystem()
                finally:
                    setSite(None)
                    setHooks()
        else:
            service._site_quota = 0


class SetQuotaAction(silvaforms.Action):
    title = _(u'Set Quota')

    def __call__(self, form, quota, line):
        data, errors = line.extractData(form.tableFields)
        if errors:
            raise silvaforms.ActionError('Invalid quota settings.')
        quota.update(data['quota'])
        return silvaforms.SUCCESS


class ManageQuotaRootForm(silvaforms.ZMISubTableForm):
    grok.context(Application)
    grok.view(ManageSiteForm)

    label = _(u'Manage sites')
    description = _(u'Modify the space (in MB) allocated to a complete Silva '
                    u'site. This setting is not modifiable from within the site.')
    ignoreContent = False
    batchSize = 25
    batchItemFactory = QuotaRootFactory
    tableFields = silvaforms.Fields(IQuotaRootManager)
    tableFields['identifier'].mode = silvaforms.DISPLAY
    tableFields['used'].mode = silvaforms.DISPLAY
    tableActions = silvaforms.TableActions(SetQuotaAction())

    def getItems(self):
        return self.context.objectValues('Silva Root')

    def getItemIdentifier(self, item, position):
        return item.identifier


class Root(Publication):
    """Root of Silva site.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Root"

    # We do not want to register Root automaticaly.
    grok.implements(IRoot)
    silvaconf.icon('icons/root.png')
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

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'validate_wanted_quota')
    def validate_wanted_quota(self, value, REQUEST=None):
        """Validate the wanted quota is correct the current
        publication.
        """
        if value < 0:
            # Quota can't be negative.
            return False
        if not value:
            # 0 or means no quota.
            return True
        # Quota can't be be bigger than the site quota.
        if self.service_extensions._site_quota:
            if self.service_extensions._site_quota < value:
                return False
        return True

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_folder')
    def to_folder(self):
        """Don't do anything here. Can't do this with root.
        """
        raise ContentError(
            _(u"Root cannot be converted to folder."), self)

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_publication')
    def to_publication(self):
        """Don't do anything here. Can't do this with root.
        """
        raise ContentError(
            _(u"Root cannot be converted to publication."), self)

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
            return False
        return meta_type in self._addables_forbidden

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_current_quota')
    def get_current_quota(self):
        """Return the current quota value on the publication.
        """
        site = getUtility(IExtensionService).get_site_quota()
        binding = getUtility(IMetadataService).getMetadata(self)
        try:
            local = int(binding.get('silva-quota', element_id='quota') or 0)
            if local < 0:
                local = 0
        except KeyError:
            local = 0
        if site and local:
            return min(site, local)
        if site:
            return site
        return local

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

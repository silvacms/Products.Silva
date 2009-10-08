# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope import interface, schema
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Globals import package_home
from DateTime import DateTime
import transaction
import zLOG

# Silva
from Products.Silva.helpers import add_and_edit
from Products.Silva.Root import DocumentationInstallationException
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.i18n import translate as _
from Products.Silva import install


from silva.core import interfaces
from silva.core.interfaces import (ISilvaObject, IVersion,
                                       IContainer, IAsset)
from silva.core.services.base import SilvaService
from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf
import os.path

class ExtensionService(SilvaService):
    meta_type = 'Silva Extension Service'

    security = ClassSecurityInfo()

    manage_options = (
        {'label':'Extensions', 'action':'manage_extensions'},
        {'label':'Partial upgrades', 'action':'manage_partialUpgrade'},
        {'label':'Partial reindex', 'action':'manage_partialReindex'},
        ) + SilvaService.manage_options

    silvaconf.icon('www/silva.png')
    silvaconf.factory('manage_addExtensionService')

    _quota_enabled = False

    def __init__(self, id, title):
        self.id = id
        self.title = title
        # Actually is the cache refresh datetime
        self._refresh_datetime = DateTime()

    # MANIPULATORS

    def _update_views(self, root):
        productsWithView = [
            inst_name for inst_name in extensionRegistry.get_names()
            if (extensionRegistry.is_installed(inst_name, root) and
                (inst_name in root.service_views.objectIds()))]
        root.service_view_registry.set_trees(productsWithView)

    security.declareProtected('View management screens', 'install')
    def install(self, name, status=None):
        """Install extension
        """
        root = self.get_root()
        extensionRegistry.install(name, root)
        self._update_views(root)
        if status:
            return '%s installed' % name

    security.declareProtected('View management screens', 'uninstall')
    def uninstall(self, name, status=None):
        """Uninstall extension
        """
        root = self.get_root()
        extensionRegistry.uninstall(name, root)
        self._update_views(root)
        if status:
            return '%s uninstalled' % name

    security.declareProtected('View management screens', 'refresh')
    def refresh(self, name, status=None):
        """Refresh  extension.  
        """
        root = self.get_root()
        extensionRegistry.refresh(name,root)
        self.refresh_caches()
        if status:
            return '%s refreshed' % name

    security.declareProtected('View management screens', 'refresh_all')
    def refresh_all(self, status=None):
        """Refreshes all extensions
        """
        for name in extensionRegistry.get_names():
            if self.is_installed(name):
                self.refresh(name)
        if status:
            return 'Silva and all installed extensions have been refreshed'

    security.declareProtected('View management screens', 'refresh_caches')
    def refresh_caches(self):
        """Refresh caches
        """
        self._refresh_datetime = DateTime()

    security.declareProtected('View management screens', 'upgrade_all')
    def upgrade_all(self, status=None):
        """Upgrades all content
        """
        self.get_root().upgrade_silva()
        if status:
            return 'Content upgrade succeeded. See event log for details'

    security.declareProtected('View management screens', 'install_layout')
    def install_layout(self, status):
        """Install core layout.
        """
        root = self.get_root()
        install.configureLayout(root, 1)
        if status:
            return 'Default layout code installed'

    security.declareProtected('View management screens',
                              'install_documentation')
    def install_documentation(self, status=None):
        """Install the doucmentation.
        """
        message = 'Documentation installed'
        try:
            self.get_root().manage_installDocumentation()
        except DocumentationInstallationException, e:
            message = e
        if status:
            return message


    security.declareProtected('View management screens',
                              'refresh_catalog')
    def refresh_catalog(self, status=None):
        """Refresh the silva catalog.
        """
        root = self.get_root()
        root.service_catalog.manage_catalogClear()
        zLOG.LOG(
            'Silva', zLOG.INFO,
            'Cleared the catalog')
        self._index(root)
        if status:
            return 'Catalog refreshed'

    security.declareProtected('View management screens',
                              'reindex_subtree')
    def reindex_subtree(self, path):
        """reindexes a subtree
        """
        root = self.get_root()
        obj = root.unrestrictedTraverse(str(path))
        self._reindex(obj)

    def _reindex(self, obj):
        """Reindex a silva object or version.
        """
        for i, object_to_index in enumerate(self._get_objects_to_reindex(obj)):
            if i and i % 500 == 0:
                transaction.get().commit()
                zLOG.LOG(
                    'Silva', zLOG.INFO,
                    '%s objects reindexed' % str(i))
            object_to_index.reindex_object()
        zLOG.LOG(
            'Silva', zLOG.INFO,
            'Catalog rebuilt. Total of %s objects reindexed' % str(i))

    def _index(self, obj):
        """index silva objects or versions.
        """
        for i, object_to_index in enumerate(self._get_objects_to_reindex(obj)):
            if i and i % 500 == 0:
                transaction.get().commit()
                zLOG.LOG(
                    'Silva', zLOG.INFO,
                    '%s objects indexed' % str(i))
            object_to_index.index_object()
        zLOG.LOG(
            'Silva', zLOG.INFO,
            'Catalog rebuilt. Total of %s objects indexed' % str(i))

    def _get_objects_to_reindex(self, obj):
        """A generator to lazily get all the objects that need to be
        reindexed."""
        if ISilvaObject.providedBy(obj) and getattr(obj, 'index_object', None):
            yield obj
        elif IVersion.providedBy(obj) and getattr(obj, 'index_object', None):
            if obj.version_status() != 'last_closed' and obj.version_status(
                ) != 'closed' :
                yield obj
        if IContainer.providedBy(obj):
            for child in obj.objectValues():
                for obj in self._get_objects_to_reindex(child):
                    yield obj

    security.declareProtected('View management screens',
                              'disable_quota_subsystem')
    def disable_quota_subsystem(self, status=None):
        """Disable quota sub-system.
        """
        assert (self._quota_enabled)

        root = self.get_root()

        # Disable metadata for quota
        collection = root.service_metadata.getCollection()
        if 'silva-quota' in collection.objectIds():
            collection.manage_delObjects(['silva-quota'])
        setids = ('silva-quota',)
        types = ('Silva Root', 'Silva Publication', )
        root.service_metadata.removeTypesMapping(types, setids)

        self._quota_enabled = False
        if status:
            return 'Quota sub-system disabled'

    security.declareProtected('View management screens',
                              'enable_quota_subsystem')
    def enable_quota_subsystem(self, status=None):
        """Enable quota sub-system.
        """
        assert (not self._quota_enabled)

        root = self.get_root()

        # Setup metadata for quota
        silva_home = package_home(globals())
        silva_docs = os.path.join(silva_home, 'doc')

        collection = root.service_metadata.getCollection()
        if 'silva-quota' in collection.objectIds():
            collection.manage_delObjects(['silva-quota'])

        xml_file = os.path.join(silva_docs, 'silva-quota.xml')
        fh = open(xml_file, 'r')
        collection.importSet(fh)

        setids = ('silva-quota',)
        types = ('Silva Root', 'Silva Publication', )
        root.service_metadata.addTypesMapping(types, setids)
        root.service_metadata.initializeMetadata()

        def visitor(item):
            total = 0
            if IContainer.providedBy(item):
                used_space = 0
                for _, obj in item.objectItems():
                    used_space += visitor(obj)
                item.used_space = used_space
                total += used_space
            elif IAsset.providedBy(item):
                try:
                    total += item.reset_quota()
                except (AttributeError, NotImplementedError):      # Well, not all asset
                                            # respect its interface.
                    path = '/'.join(item.getPhysicalPath())
                    klass = str(item.__class__)
                    zLOG.LOG('Silva quota', zLOG.WARNING,
                             'bad asset object %s - %s' % (path, klass))
            return total

        root = self.get_root()
        root.used_space = visitor(root)
        self._quota_enabled = True
        if status:
            return 'Quota sub-system enabled'


    # ACCESSORS

    security.declareProtected(
        'Access contents information', 'get_quota_subsystem_status')
    def get_quota_subsystem_status(self):
        return self._quota_enabled

    security.declareProtected(
        'Access contents information', 'is_installed')
    def is_installed(self, name):
        """Is extension installed?
        """
        root = self.get_root()
        return extensionRegistry.is_installed(name, root)

    security.declareProtected(
        'View management screens', 'get_refresh_datetime')
    def get_refresh_datetime(self):
        """Get datetime of last refresh.
        """
        return self._refresh_datetime

InitializeClass(ExtensionService)

def manage_addExtensionService(self, id, title='', REQUEST=None):
    """Add extension service."""
    object = ExtensionService(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''


class IPartialUpgrade(interface.Interface):
    """Data needed to do a partial upgrade.
    """

    path = schema.TextLine(
        title=_(u"Absolute path to object to upgrade"),
        required=True)
    version = schema.TextLine(
        title=_(u"Current Silva version of the object"),
        required=True)


class PartialUpgradesForm(silvaviews.ZMIForm):

    silvaconf.name('manage_partialUpgrade')

    form_fields = grok.Fields(IPartialUpgrade)
    description = _(u"Below you find a form that allows you to specify "
                    u"an object to upgrade, and which version the object "
                    u"is in now. When you enter values in those fields and "
                    u"press the 'upgrade' button, Silva will try to upgrade "
                    u"the object to get it in proper shape for the current "
                    u"Silva version. Note that this functionality is "
                    u"experimental, and it is known that performing a "
                    u"partial upgrade on an object may fail and may "
                    u"even (in some situations) cause the object to "
                    u"become unusable.")

    @grok.action(_("Upgrade"))
    def action_upgrade(self, path, version):
        root = self.context.get_root()
        #path is unicode; it needs to either be a string, or split
        path = path.encode('utf-8')
        root.upgrade_silva_object(version, path)
        self.status = _(u"Content upgrade succeeded. See event log for details")


class IPartialReindex(interface.Interface):
    """Information needed to partially reindex a site.
    """

    path = schema.TextLine(
        title=_(u"Absolute path to reindex"),
        required=True)


class PartialReindexForm(silvaviews.ZMIForm):

    silvaconf.name('manage_partialReindex')

    form_fields = grok.Fields(IPartialReindex)
    description = _(u"Reindex a subtree of the site in the Silva Catalog."
                    u"For big trees this may take a long time.")

    @grok.action(_("Reindex"))
    def action_reindex(self, path):
        try:
            self.context.reindex_subtree(path)
        except KeyError:
            self.status = _(u"Invalid path")
        else:
            self.status = _(u"Partial catalog refreshed")


class ManageExtensions(silvaviews.ZMIView):

    silvaconf.name('manage_extensions')

    status = None

    def update(self):
        methods = ['refresh_all', 'install_documentation',
                   'refresh_catalog', 'disable_quota_subsystem',
                   'enable_quota_subsystem', 'upgrade_all', 'install_layout']
        for method in methods:
            if method in self.request.form:
                self.status = getattr(self.context, method)(status=True)
        else:
            if 'name' in self.request.form:
                methods = ['install', 'uninstall', 'refresh']
                for method in methods:
                    if method in self.request.form:
                        self.status = getattr(self.context, method)(self.request.form['name'], status=True)

    def extensions(self):
        names = extensionRegistry.get_names()
        for name in names:
            extension = extensionRegistry.get_extension(name)
            if not interfaces.ISystemExtension.providedBy(extension):
                yield extension

    def system_extensions(self):
        names = extensionRegistry.get_names()
        for name in names:
            extension = extensionRegistry.get_extension(name)
            if interfaces.ISystemExtension.providedBy(extension):
                yield extension

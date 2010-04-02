# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope import interface, schema
from five import grok

from datetime import datetime
import os.path
import logging

# Zope 2
from AccessControl import ClassSecurityInfo
from App.Common import package_home
from App.class_init import InitializeClass
from DateTime import DateTime
from OFS.Folder import Folder
from OFS.Image import manage_addFile
import transaction

# Silva
from Products.Silva.helpers import add_and_edit
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva import install

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.services.base import SilvaService
from silva.core.services.interfaces import ICataloging
from silva.core.upgrade import upgrade
from silva.core.views import views as silvaviews
from silva.translations import translate as _


logger = logging.getLogger('silva.core')


def get_content_to_index(self, content):
    """A generator to lazily get all the objects that need to be
    indexed.
        """
    if interfaces.ISilvaObject.providedBy(content):
        # Version are indexed by the versioned content itself
        yield content
    if interfaces.IContainer.providedBy(content):
        for child in content.objectValues():
            for content in get_content_to_index(child):
                yield content


def index_content(self, obj, reindex=False):
    """Recursively index or index Silva Content.
    """
    for count, content in enumerate(get_content_to_index(obj)):
        if count and count % 500 == 0:
            transaction.commit()
            logger.info('indexing: %d objects indexed' % count)
        if reindex:
            ICataloging(content).reindex()
        else:
            ICataloging(content).index()
    logger.info('catalog indexing: %d objects indexed' % count)


def compute_used_space(content):
    """Recursively compute the used space by asset in the given content.
    """
    total = 0
    if interfaces.IContainer.providedBy(content):
        used_space = 0
        for obj in content.objectValues():
            if ISilvaObject.providedBy(obj):
                used_space += compute_used_space(obj)
        content.used_space = used_space
        total += used_space
    elif interfaces.IAsset.providedBy(content):
        try:
            total += content.reset_quota()
        except (AttributeError, NotImplementedError):
            # Well, not all asset respect its interface.
            path = '/'.join(content.getPhysicalPath())
            klass = str(content.__class__)
            logger.error('bad asset object %s - %s' % (path, klass))
    return total


def install_documentation(container):
    """Install documentation in the given container.
    """
    documentation_path = os.path.join(
        os.path.dirname(__file__), 'doc', 'silva_docs.zip')
    with open(documentation_path, 'rb') as documentation:
        interfaces.IZipfileImporter(container).importFromZip(
            container, documentation)


class ExtensionService(Folder, SilvaService):
    meta_type = 'Silva Extension Service'

    security = ClassSecurityInfo()

    manage_options = (
        {'label':'Extensions', 'action':'manage_extensions'},
        {'label':'Partial upgrades', 'action':'manage_partialUpgrade'},
        {'label':'Partial reindex', 'action':'manage_partialReindex'},
        {'label': 'Logs', 'action':'manage_main'},
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

    security.declareProtected(
        'View management screens', 'install')
    def install(self, name):
        """Install extension
        """
        root = self.get_root()
        extensionRegistry.install(name, root)
        self._update_views(root)

    security.declareProtected(
        'View management screens', 'uninstall')
    def uninstall(self, name):
        """Uninstall extension
        """
        root = self.get_root()
        extensionRegistry.uninstall(name, root)
        self._update_views(root)

    security.declareProtected(
        'View management screens', 'refresh')
    def refresh(self, name):
        """Refresh  extension.
        """
        root = self.get_root()
        extensionRegistry.refresh(name,root)
        self.refresh_caches()

    security.declareProtected(
        'View management screens', 'refresh_all')
    def refresh_all(self):
        """Refreshes all extensions
        """
        for name in extensionRegistry.get_names():
            if self.is_installed(name):
                self.refresh(name)

    security.declareProtected('View management screens', 'refresh_caches')
    def refresh_caches(self):
        """Refresh caches
        """
        self._refresh_datetime = DateTime()

    security.declareProtected(
        'View management screens', 'refresh_catalog')
    def refresh_catalog(self):
        """Refresh the silva catalog.
        """
        root = self.get_root()
        root.service_catalog.manage_catalogClear()
        logger.info('Catalog cleared.')
        index_content(root)

    security.declareProtected(
        'View management screens', 'reindex_subtree')
    def reindex_subtree(self, path):
        """reindexes a subtree.
        """
        root = self.get_root()
        index_content(root.unrestrictedTraverse(str(path)), reindex=True)

    security.declareProtected(
        'View management screens', 'disable_quota_subsystem')
    def disable_quota_subsystem(self):
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

    security.declareProtected(
        'View management screens', 'enable_quota_subsystem')
    def enable_quota_subsystem(self):
        """Enable quota sub-system.
        """
        assert (not self._quota_enabled)
        root = self.get_root()

        # Setup metadata for quota
        silva_docs = os.path.join(os.path.dirname(__file__), 'doc')

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

        root.used_space = compute_used_space(root)
        self._quota_enabled = True

    security.declareProtected(
        'View management screens', 'upgrade_content')
    def upgrade_content(self, content, from_version, to_version):
        """Upgrade the given content
        """
        now = datetime.now().strftime('%Y-%b-%dT%H%M%S')
        log_filename = 'upgrade-log-%s-to-%s-on-%s.log' % (
            from_version, to_version, now)
        log = upgrade.registry.upgrade(content, from_version, to_version)
        manage_addFile(
            self, log_filename, log.encode('utf-8'), content_type='text/plain')
        if interfaces.IRoot.providedBy(content):
            content._content_version = to_version


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
    """From to partially upgrade a site. TO USE ONLY if you known what
    you are doing.
    """
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
        # If path is an unicode string it need to be encoded.
        path = path.encode('utf-8')
        content = root.restrictedTraverse(path)
        self.context.upgrade_content(
            content, version, root.get_silva_software_version())
        self.status = _(u"Content upgrade succeeded. See event log for details")


class IPartialReindex(interface.Interface):
    """Information needed to partially reindex a site.
    """
    path = schema.TextLine(
        title=_(u"Absolute path to reindex"),
        required=True)


class PartialReindexForm(silvaviews.ZMIForm):
    """From to partially reindex a part of the site.
    """
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
    """Form to activate, deactivate, refresh extensions.
    """
    silvaconf.name('manage_extensions')
    status = None

    def refresh_all(self):
        self.context.refresh_all()
        return _(u'Silva and all installed extensions have been refreshed')

    def refresh_catalog(self):
        self.context.refresh_catalog()
        return _(u'Catalog refreshed')

    def disable_quota_subsystem(self):
        self.context.disable_quota_subsystem()
        return _(u'Quota sub-system disabled')

    def enable_quota_subsystem(self):
        self.context.enable_quota_subsystem()
        return _(u'Quota sub-system enabled')

    def upgrade_all(self):
        root = self.context.get_root()
        from_version = root.get_silva_content_version()
        to_version = root.get_silva_software_version()
        self.context.upgrade_content(root, from_version, to_version)
        return  _(u'Content upgrade succeeded. See log in Logs tab for details')

    def install_documentation(self):
        install_documentation(self.context.get_root())
        return _(u'Documentation installed')

    def install_layout(self):
        root = self.context.get_root()
        install.configureLegacyLayout(root, 1)
        return _(u'Default legacy layout code installed')

    def install(self, name):
        self.context.install(name)
        return '%s installed' % name

    def uninstall(self, name):
        self.context.uninstall(name)
        return '%s uninstalled' % name

    def refresh(self, name):
        self.context.refresh(name)
        return '%s refreshed' % name

    def update(self):
        methods = ['refresh_all', 'install_documentation',
                   'refresh_catalog', 'disable_quota_subsystem',
                   'enable_quota_subsystem', 'upgrade_all', 'install_layout']
        for method in methods:
            if method in self.request.form:
                self.status = getattr(self, method)()
        else:
            if 'name' in self.request.form:
                methods = ['install', 'uninstall', 'refresh']
                for method in methods:
                    if method in self.request.form:
                        self.status = getattr(self.context, method)(
                            self.request.form['name'])

    def extensions(self):
        """Return non-system extensions
        """
        names = extensionRegistry.get_names()
        for name in names:
            extension = extensionRegistry.get_extension(name)
            if not interfaces.ISystemExtension.providedBy(extension):
                yield extension

    def system_extensions(self):
        """Return system extensions
        """
        names = extensionRegistry.get_names()
        for name in names:
            extension = extensionRegistry.get_extension(name)
            if interfaces.ISystemExtension.providedBy(extension):
                yield extension

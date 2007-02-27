# silva imports
import zLOG
from zope import interface
from Products.Silva import mangle
from Products.Silva.interfaces import IUpgrader, IInvisibleService
from Products.Silva.adapters.interfaces import IIndexable
from Products.Silva.interfaces import IVersionedContent, IRoot, ISilvaObject
from Products.Silva.interfaces import IVersion
from Products.Silva.adapters import version_management

from Products.Silva import upgrade

def initialize():
    upgrade.registry.registerUpgrader(
        IndexerUpgrader(), '1.6', 'Silva Indexer')
    upgrade.registry.registerUpgrader(
        AutoTOCUpgrader(), '1.6', 'Silva AutoTOC')
    upgrade.registry.registerUpgrader(
        IndexItemUpgrader(), '1.6', upgrade.AnyMetaType)
    upgrade.registry.registerUpgrader(
        CatalogRefresher(), '1.6', upgrade.AnyMetaType)
    upgrade.registry.registerUpgrader(
        InvisibleMan(), '1.6', upgrade.AnyMetaType)
    
class IndexItemUpgrader:

    interface.implements(IUpgrader)

    def upgrade(self, obj):
        # <index name="foo" /> to
        # <index name="foo" title="foo"/>
        if IVersionedContent.providedBy(obj):
            vm = version_management.getVersionManagementAdapter(obj)
            for version in vm.getVersions():
                if hasattr(version, 'content'):
                    dom = version.content
                    if hasattr(dom, 'documentElement'):
                        self._upgrade_helper(dom.documentElement)
        else:
            try:
                indexable = IIndexable(obj)
            except:
                return obj
            if not hasattr(obj, 'content'):
                return obj
            dom = obj.content
            self._upgrade_helper(dom.documentElement)
        return obj

    def _upgrade_helper(self, node):
        if node.nodeType == node.ELEMENT_NODE and node.nodeName == 'index':
            old_name_node = node.attributes.get('name', None)
            if old_name_node is not None:
                old_name = node.attributes['name'].value
            else:
                old_name = ''
            title = node.attributes.get('title', None)
            if not title:
                node.setAttribute('title', old_name)
            elif not title.value:
                node.setAttribute('title', old_name)
            node.setAttribute('name', mangle.generateAnchorName(old_name))
        else:
            for child in node.childNodes:
                self._upgrade_helper(child)
    
    
class IndexerUpgrader:

    interface.implements(IUpgrader)
    
    def upgrade(self, indexer):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            'Upgrading Indexer: %s' % indexer.get_title_or_id())
        indexer.update()
        return indexer

class AutoTOCUpgrader:

    interface.implements(IUpgrader)
    
    def upgrade(self, autotoc):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            'Upgrading AutoTOC: %s' % autotoc.get_title_or_id())
        if not hasattr(autotoc, '_toc_depth'):
            autotoc._toc_depth = -1
        return autotoc
    
class CatalogRefresher:
    """Refreshes the whole Silva catalog"""
    interface.implements(IUpgrader)

    def upgrade(self, obj):
        if IRoot.providedBy(obj):
            # Clear the Silva catalog
            zLOG.LOG('Silva', zLOG.INFO, 'Catalog Refresh: clearing catalog and reindexing all content. This may take a long time.')
            obj.service_catalog.manage_catalogClear()
        elif ISilvaObject.providedBy(obj) and getattr(obj, 'index_object', None):
            obj.index_object()
        elif IVersion.providedBy(obj) and getattr(obj, 'index_object', None):
            if obj.version_status() != 'last_closed' and \
               obj.version_status() != 'closed' :
                obj.index_object()
        return obj

class InvisibleMan:
    """Makes Widget Registry services invisible by putting a marker
    interface on them."""
    interface.implements(IUpgrader)
    
    names = ['service_doc_editor', 'service_doc_previewer',
             'service_doc_viewer',
             'service_field_editor', 'service_field_viewer',
             'service_nlist_editor', 'service_nlist_previewer',
             'service_nlist_viewer',
             'service_sub_editor', 'service_sub_previewer',
             'service_sub_viewer',
             'service_table_editor', 'service_table_viewer',

             'service_annotations']

    def upgrade(self, obj):
        if IRoot.providedBy(obj):
            for name in self.names:
                service = getattr(obj.aq_explicit, name, None)
                if service is not None:
                    interface.directlyProvides(
                        service,
                        IInvisibleService,
                        interface.directlyProvidedBy(obj[name]))
        return obj

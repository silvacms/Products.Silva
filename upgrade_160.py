# silva imports
import zLOG
from zope.interface import implements
from Products.Silva import mangle
from Products.Silva.interfaces import IUpgrader
from Products.Silva.adapters.interfaces import IIndexable
from Products.Silva.interfaces import IVersionedContent
from Products.Silva.adapters import version_management

from Products.Silva import upgrade

def initialize():
    upgrade.registry.registerUpgrader(
        IndexerUpgrader(), '1.6', 'Silva Indexer')
    upgrade.registry.registerUpgrader(
        IndexItemUpgrader(), '1.6', upgrade.AnyMetaType)

class IndexItemUpgrader:

    implements(IUpgrader)

    def upgrade(self, obj):
        # <index name="foo" /> to
        # <index name="foo" title="foo"/>
        if IVersionedContent.providedBy(obj):
            vm = version_management.getVersionManagementAdapter(obj)
            for version in vm.getVersions():
                dom = version.content
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
            old_name = node.attributes['name'].value
            node.setAttribute('title', old_name)
            node.setAttribute('name', mangle.generateAnchorName(old_name))
        else:
            for child in node.childNodes:
                self._upgrade_helper(child)
    
    
class IndexerUpgrader:

    implements(IUpgrader)
    
    def upgrade(self, indexer):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            'Upgrading Indexer: %s' % indexer.get_title_or_id())
        indexer.update()
        return indexer

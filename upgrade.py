
from zope.interface import implements
# zope imports
import zLOG
import DateTime
import transaction

# silva imports
from Products.Silva.interfaces import ISilvaObject, IContainer, IUpgrader
from Products.Silva import mangle

threshold = 500

class GeneralUpgrader:
    """wrapper for upgrade functions"""
    
    implements(IUpgrader)

    def __init__(self, upgrade_handler):
        """constructor

            upgrade_handler: function which actually does the upgrade
                one argument: the object to be upgraded
        """
        self._upgrade_handler = upgrade_handler

    def upgrade(self, obj):
        new_object = self._upgrade_handler(obj)
        if new_object:
            return new_obj
        return obj
   
    def __repr__(self):
        return "<GeneralUpgrader %r>" % self._upgrade_handler

# marker for upgraders to be called for any object
class AnyMetaType:
    pass
AnyMetaType = AnyMetaType()

class UpgradeRegistry:
    """Here people can register upgrade methods for their objects
    """
    
    def __init__(self):
        self.__registry = {}
        self._setUp = {}
        self._tearDown = {}
    
    def register(self, meta_type, upgrade_handler, version):
        """Register a meta_type for upgrade.

        The upgrade handler is called with the object as its only argument
        when the upgrade script encounters an object of the specified
        meta_type.
        """
        self.registerFunction(upgrade_handler, version, meta_type)

    def registerFunction(self, function, version, meta_type):
        upgrader = GeneralUpgrader(function)
        self.registerUpgrader(upgrader, version, meta_type)
        

    def registerUpgrader(self, upgrader, version, meta_type):
        assert IUpgrader.providedBy(upgrader)
        self.__registry.setdefault(version, {}).setdefault(meta_type, []).\
            append(upgrader)

    def registerSetUp(self, function, version):
        self._setUp.setdefault(version, []).append(function)

    def registerTearDown(self, function, version):
        self._tearDown.setdefault(version, []).append(function)
        
    def getUpgraders(self, version, meta_type):
        """Return the registered upgrade_handlers of meta_type
        """
        upgraders = []
        v_mt = self.__registry.get(version, {})
        upgraders.extend(v_mt.get(meta_type, []))
        upgraders.extend(v_mt.get(AnyMetaType, []))
        return upgraders

    def upgradeObject(self, obj, version):
        mt = obj.meta_type
        for upgrader in self.getUpgraders(version, mt):
            zLOG.LOG('Silva', zLOG.BLATHER, 
                'Upgrading %s' % obj.absolute_url(),
                'Upgrading with %r' % upgrader)
            # sometimes upgrade methods will replace objects, if so the
            # new object should be returned so that can be used for the rest
            # of the upgrade chain instead of the old (probably deleted) one
            obj = upgrader.upgrade(obj)
            assert obj is not None, "Upgrader %r seems to be broken, "\
                "this is a bug." % (upgrader, )
        return obj
        
    def upgradeTree(self, root, version):
        """upgrade a whole tree to version"""
        stats = {
            'total': 0,
            'threshold': 0,
            'starttime': DateTime.DateTime(),
            'endtime': None,
            'maxqueue' : 0,
            }
        
        self.setUp(root, version)
        object_list = [root]
        try:
            while object_list:
                o = object_list[-1]
                del object_list[-1]
                #print 'Upgrading object', o.absolute_url(), '(still %s objects to go)' % len(object_list)
                o = self.upgradeObject(o, version)
                if hasattr(o.aq_base, 'objectValues'):
                    if o.meta_type == "Parsed XML":
                        #print '#### Skip the Parsed XML object'
                        pass
                    else:
                        object_list.extend(o.objectValues())
                        stats['maxqueue'] = max(stats['maxqueue'],
                                                len(object_list))
                stats['total'] += 1
                stats['threshold'] += 1                
                if stats['threshold'] > threshold:
                    #print '#### Commit sub transaction ####'
                    transaction.get().commit(1)
                    if hasattr(o, '_p_jar') and o._p_jar is not None:
                        o._p_jar.cacheGC()
                    else:
                        #print 'No _p_jar, or it is None for', repr(o)
                        pass
                    stats['threshold'] = 0
            stats['endtime'] = DateTime.DateTime()
            self.tearDown(root, version)
        finally:
            #print repr(stats)
            pass

    def upgrade(self, root, from_version, to_version):
        zLOG.LOG('Silva', zLOG.INFO, 'Upgrading content from %s to %s.' % (
            from_version, to_version))
        versions = self.__registry.keys()
        versions.sort(lambda x, y: cmp(self._vers_str_to_int(x),
            self._vers_str_to_int(y)))
            
        # XXX this code is confusing, but correct. We might want to redo
        # the whole version-registry-upgraders-shebang into something more
        # understandable.
            
        try:
            version_index = versions.index(from_version)
        except ValueError:
            zLOG.LOG(
                'Silva', zLOG.WARNING, 
                ("Nothing can be done: there's no upgrader registered to "
                 "upgrade from %s to %s.") % (from_version, to_version)
                )
            return
        else:
            upgrade_chain = [ v
                for (v, i) in zip(versions, range(len(versions)))
                if i > version_index
                ]
        if not upgrade_chain:
            zLOG.LOG('Silva', zLOG.INFO, 'Nothing needs to be done.')
        for version in upgrade_chain:
            zLOG.LOG('Silva', zLOG.INFO, 'Upgrading to version %s.' % version)
            self.upgradeTree(root, version)
        zLOG.LOG('Silva', zLOG.INFO, 'Upgrade finished.')
        
    def setUp(self, root, version):
        for function in self._setUp.get(version, []):
            function(root)
    
    def tearDown(self, root, version):
        for function in self._tearDown.get(version, []):
            function(root)

    def _vers_str_to_int(self, version):
        return tuple([ int(s) for s in version.split('.') ])

    def _vers_int_to_str(self, version):
        return '.'.join([ str(i) for i in version ])
        
registry = UpgradeRegistry()

def check_reserved_ids(obj):
    """Walk through the entire tree to find objects of which the id is not
    allowed, and return a list of the urls of those objects
    """
    #print 'checking for reserved ids on', repr(obj)
    object_list = obj.objectValues()
    while object_list:
        o = object_list[0]
        del object_list[0]
        if IContainer.providedBy(o):
            object_list.extend(o.objectValues())
        if not ISilvaObject.providedBy(o):
            continue
        old_id = o.getId()
        id = mangle.Id(o.aq_parent, old_id, allow_dup=1)
        if id.isValid():
            continue
        id.cook()
        while not id.isValid():
            id = mangle.Id(o.aq_parent, 'renamed_%s' % id, allow_dup=0)
        o.aq_parent.manage_renameObject(old_id, str(id))
        zLOG.LOG("Silva", zLOG.INFO,
            'Invalid id %s found. Renamed to %s' % (repr(old_id), repr(id)),
            'Location: %s' % o.absolute_url())


# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from bisect import insort_right
from pkg_resources import parse_version

# Zope
from zope.interface import implements
import zLOG
import DateTime
import transaction

# Silva
from silva.core.interfaces import IUpgrader, IUpgradeRegistry, IRoot

threshold = 50

# marker for upgraders to be called for any object
AnyMetaType = object()

class BaseUpgrader(object):
    """All upgrader should inherit from this upgrader.
    """

    implements(IUpgrader)

    def __init__(self, version, meta_type, priority=0):
        self.version = version
        self.meta_type = meta_type
        self.priority = priority

    def upgrade(self, obj):
        raise NotImplementedError

    def __cmp__(self, other):
        sort = cmp(self.priority, other.priority)
        if sort == 0:
            sort = cmp(self.__class__.__name__,
                       other.__class__.__name__)
        return sort


class BaseRefreshAll(BaseUpgrader):
    """Refresh all products.
    """

    def upgrade(self, root):
        zLOG.LOG('Silva', zLOG.INFO, 'refresh all installed products')
        root.service_extensions.refresh_all()
        return root


def get_version_index(version_list, wanted_version):
    """Return the index of the version in the list.
    """
    try:
        dev_index = wanted_version.index('dev')
        wanted_version = wanted_version[:dev_index]
    except ValueError:
        # It's not a development version everything is ok.
        pass
    wanted_version = parse_version(wanted_version)
    for index, version in enumerate(version_list):
        parsed_version = parse_version(version)
        if wanted_version < parsed_version:
            return index
        elif wanted_version == parsed_version:
            return index + 1
    # Version outside of scope, return the last upgrader.
    return index + 1


def get_upgrade_chain(versions, from_version, to_version):
    """Return a list of version to upgrade to when upgrading from to
    to version.
    """
    versions.sort(lambda x, y: cmp(parse_version(x), parse_version(y)))
    version_start_index = get_version_index(versions, from_version)
    version_end_index = get_version_index(versions, to_version)
    return versions[version_start_index:version_end_index]


class UpgradeRegistry(object):
    """Here people can register upgrade methods for their objects
    """

    implements(IUpgradeRegistry)

    def __init__(self):
        self.__registry = {}
        self._setUp = {}
        self._tearDown = {}

    def registerUpgrader(self, upgrader, version=None, meta_type=None):
        assert IUpgrader.providedBy(upgrader)
        if not version:
            version = upgrader.version
        if not meta_type:
            meta_type = upgrader.meta_type
        if isinstance(meta_type, str) or meta_type is AnyMetaType:
            meta_type = [meta_type,]
        for type_ in meta_type:
            registry = self.__registry.setdefault(version, {}).setdefault(type_, [])
            insort_right(registry, upgrader)

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
            if getattr(obj, 'absolute_url', None):
                # Not all objects have an absolute_url ...
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

    def upgradeTree(self, root, version, ignore_root=False):
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
                # print 'Upgrading object', o.absolute_url(), '(still
                # %s objects to go)' % len(object_list)
                if not (ignore_root and IRoot.providedBy(o)):
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
                #print '#### threshold subtotal: %s, total: %s ####' % (
                #    stats['threshold'], stats['total'])
                if stats['threshold'] > threshold:
                    #print '#### Commit sub transaction ####'
                    transaction.get().commit()
                    if hasattr(o, '_p_jar') and o._p_jar is not None:
                        o._p_jar.cacheGC()
                    stats['threshold'] = 0
            stats['endtime'] = DateTime.DateTime()
            self.tearDown(root, version)
        finally:
            #print repr(stats)
            pass

    def upgrade(self, root, from_version, to_version):
        zLOG.LOG('Silva', zLOG.INFO, 'Upgrading content from %s to %s.' % (
            from_version, to_version))
        upgrade_chain = get_upgrade_chain(self.__registry.keys(),
                                          from_version, to_version)
        if not upgrade_chain:
            zLOG.LOG('Silva', zLOG.INFO, 'Nothing needs to be done.')
        for version in upgrade_chain:
            self.upgradeObject(root, version)
        zLOG.LOG('Silva', zLOG.INFO, 'Refreshing all installed extensions.')
        root.service_extensions.refresh_all()
        for version in upgrade_chain:
            zLOG.LOG('Silva', zLOG.INFO, 'Upgrading to version %s.' % version)
            self.upgradeTree(root, version, ignore_root=True)
        zLOG.LOG('Silva', zLOG.INFO, 'Upgrade finished.')

    def setUp(self, root, version):
        for function in self._setUp.get(version, []):
            function(root)

    def tearDown(self, root, version):
        for function in self._tearDown.get(version, []):
            function(root)


registry = UpgradeRegistry()


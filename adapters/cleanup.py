# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime
import transaction

from Products.Silva import SilvaPermissions
from Products.Silva.adapters import adapter
from silva.core import interfaces as silvaInterfaces


module_security = ModuleSecurityInfo('Products.Silva.adapters.cleanup')

# when calling 'cleanup_all_old' this will have another element, 'last_closed'
statistics_template = {
    'total': 0,
    'total_versions': 0,
    'total_cleaned': 0,
    'threshold': 0,
    'max_versions': 0,
    'starttime': DateTime(),
    'endtime': DateTime(),
    }

threshold = 500 # commit sub transaction after having touched this many objects

class CleanupAdapter(adapter.Adapter):
    """
    """
    security = ClassSecurityInfo()

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                                'cleanup')
    def cleanup(self):
        """Removes all closed versions but the one that's 'last_closed'"""
        pass

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                                'cleanup_all_old')
    def cleanup_all_old(self):
        """Removes all closed versions, if possible

            this leaves the last closed alone if it's the only version of
            the VersionedContent object, if not it removes that too
        """

InitializeClass(CleanupAdapter)

class VersionedContentCleanupAdapter(CleanupAdapter):
    """ Remove unreachable version objects
    """

    def cleanup(self, statistics=None, dt=None):
        if statistics is None:
            statistics = statistics_template.copy()
        pvs = self.context._previous_versions
        if pvs is None:
            return statistics
        getMetadataValue = self.context.service_metadata.getMetadataValue
        removable_versions = []
        keep_versions = []
        for candidate in pvs[:-1]:
            version = getattr(self.context, candidate[0], None)
            # shouldn't happen: unknown version still listed as old version
            if version is None:
                continue
            version_dt = getMetadataValue(
                version, 'silva-extra', 'modificationtime')
            # can only remove those old versions that are really old
            # enough
            if dt is None or version_dt <= dt:
                removable_versions.append(candidate)
            else:
                keep_versions.append(candidate)
        # always keep the last closed version
        if pvs:
            keep_versions.append(pvs[-1])

        #removable_versions = pvs[:-1] # get older versions
        self._previous_versions = keep_versions # pvs[-1:] # keep the last one

        contained_ids = self.context.objectIds()

        removable_version_ids = [
            str(version[0]) for version in removable_versions
            if version[0] in contained_ids]

        statistics['total'] += 1
        statistics['threshold'] += 1

        if removable_version_ids:
            print 'removing old versions for %s %s' %  (
                '/'.join(self.context.getPhysicalPath()), removable_version_ids)
            statistics['total_cleaned'] += 1
            statistics['total_versions'] += len(removable_version_ids)
            statistics['max_versions'] = max(
                statistics['max_versions'], len(removable_version_ids))
            seen_ids = []
            for id in removable_version_ids:
                # skip ids we've already seen
                if id in seen_ids:
                    print "Duplicate old verion:", id
                    continue
                v = self.context._getOb(id, self.context)
                self.context._delObject(id)
                seen_ids.append(id)

        statistics['endtime'] = DateTime()
        return statistics

    def cleanup_all_old(self, statistics=None):
        stats = self.cleanup(statistics)
        if not stats.has_key('last_closed'):
            stats['last_closed'] = 0
        if self.context.get_previewable():
            # we can remove last_closed too
            lc = self.context.get_last_closed()
            if lc is not None:
                print ('removing last closed version of',
                        '\n'.join(self.context.getPhysicalPath()))
                self.context.manage_delObjects([lc.id])
                # any other closed versions should have been removed
                # by self.cleanup() so we can safely remove the whole
                # list of previous versions
                self.context._previous_versions = None
                stats['last_closed'] += 1
        return stats

class ContainerCleanupAdapter(CleanupAdapter):
    """ Delete all versions from the current location downward
    """

    def cleanup(self, statistics=None, dt=None):
        """remove all but last closed versions"""
        return self._cleanup(statistics, dt=dt)

    def cleanup_all_old(self, statistics=None):
        """remove all old versions, if possible

            leaves the last closed version in tact if it's the only contained
            version
        """
        return self._cleanup(statistics, 'cleanup_all_old')

    def _cleanup(self, statistics, remove_method='cleanup', dt=None):
        if statistics is None:
            statistics = statistics_template.copy()

        for obj in self.context.objectValues():
            adapter = getCleanupVersionsAdapter(obj)
            if adapter is not None:
                if statistics['threshold'] > threshold:
                    print 'commit sub transaction'
                    transaction.get().commit()
                    self.context._p_jar.cacheGC()
                    statistics['threshold'] = 0
                getattr(adapter, remove_method)(statistics, dt=dt)

        statistics['endtime'] = DateTime()
        return statistics

module_security.declareProtected(SilvaPermissions.ViewManagementScreens,
                                    'getCleanupVersionsAdapter')
def getCleanupVersionsAdapter(context):
    if silvaInterfaces.IContainer.providedBy(context):
        return ContainerCleanupAdapter(context).__of__(context)
    elif silvaInterfaces.IVersioning.providedBy(context):
        return VersionedContentCleanupAdapter(context).__of__(context)
    else:
        return None


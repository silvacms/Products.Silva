# Copyright (c) 2002-2006 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: cleanup.py,v 1.10 2006/01/24 16:12:01 faassen Exp $
#
import Globals
import transaction
from Acquisition import aq_parent, aq_inner
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
from Products.Silva import SilvaPermissions
from Products.Silva import roleinfo
from Products.Silva import interfaces as silvaInterfaces
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces

from DateTime import DateTime
from types import ListType

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
    
Globals.InitializeClass(CleanupAdapter)

class VersionedContentCleanupAdapter(CleanupAdapter):
    """ Remove unreachable version objects
    """
    
    def cleanup(self, statistics=None):
        if statistics is None:
            statistics = statistics_template.copy()
        
        pvs = self.context._previous_versions        
        if pvs is None:
            return statistics
                
        removable_versions = pvs[:-1] # get older versions
        self._previous_versions = pvs[-1:] # keep the last one
        
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
            self.context.manage_delObjects(removable_version_ids)                        
            
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
    
    def cleanup(self, statistics=None, all_old=False):
        """remove all but last closed versions"""
        return self._cleanup(statistics)

    def cleanup_all_old(self, statistics=None):
        """remove all old versions, if possible

            leaves the last closed version in tact if it's the only contained
            version
        """
        return self._cleanup(statistics, 'cleanup_all_old')
    
    def _cleanup(self, statistics, remove_method='cleanup'):
        if statistics is None:
            statistics = statistics_template.copy()
        
        for obj in self.context.objectValues():
            adapter = getCleanupVersionsAdapter(obj)
            if adapter is not None:                                
                if statistics['threshold'] > threshold:
                    print 'commit sub transaction'
                    transaction.get().commit(1)
                    self.context._p_jar.cacheGC()
                    statistics['threshold'] = 0
                getattr(adapter, remove_method)(statistics)
                
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
    

# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: cleanup.py,v 1.2 2003/11/11 17:14:58 jw Exp $
#
import Globals
from Acquisition import aq_parent, aq_inner
from AccessControl import ModuleSecurityInfo
from Products.Silva import SilvaPermissions
from Products.Silva import roleinfo
from Products.Silva import interfaces as silvaInterfaces
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces

from DateTime import DateTime
from types import ListType

module_security = ModuleSecurityInfo('Products.Silva.adapters.cleanup')

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
    def cleanup(self):
        pass    

class VersionedContentCleanupAdapter(CleanupAdapter):
    """ Remove unreachable version objects
    """
    
    def cleanup(self, statistics=None):
        if statistics is None:
            statistics = statistics_template.copy()
        
        pvs = self.context._previous_versions        
        if pvs is None:
            return
                
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

class ContainerCleanupAdapter(CleanupAdapter):
    """ Delete all versions from the current location downward
    """
    
    def cleanup(self, statistics=None):
        if statistics is None:
            statistics = statistics_template.copy()
        
        for obj in self.context.objectValues():
            adapter = getCleanupVersionsAdapter(obj)
            if adapter is not None:                                
                if statistics['threshold'] > threshold:
                    print 'commit sub transaction'
                    get_transaction().commit(1)
                    self.context._p_jar.cacheGC()
                    statistics['threshold'] = 0
                adapter.cleanup(statistics)
                
        statistics['endtime'] = DateTime()
        return statistics
    
module_security.declareProtected(
    SilvaPermissions.ApproveSilvaContent, 'getCleanupVersionsAdapter')    
def getCleanupVersionsAdapter(context):
    if silvaInterfaces.IContainer.isImplementedBy(context):
        return ContainerCleanupAdapter(context).__of__(context)
    elif silvaInterfaces.IVersioning.isImplementedBy(context):
        return VersionedContentCleanupAdapter(context).__of__(context)
    else:
        return None
    
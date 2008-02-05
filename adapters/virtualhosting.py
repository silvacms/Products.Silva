# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: virtualhosting.py,v 1.8 2006/01/24 16:12:01 faassen Exp $
#
import Globals
from Acquisition import aq_parent, aq_inner
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo,\
     getSecurityManager
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.Permission import Permission
from Products.Silva import SilvaPermissions
from Products.Silva import roleinfo
from Products.Silva import interfaces as silva_interfaces
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces

from DateTime import DateTime

class VirtualHostingAdapter(adapter.Adapter):
    """ Virtual Hosting adapter
    """
    
    def getVirtualRootPhysicalPath(self):
        """ Get the physical path of the object being the 
        virtual host root.
    
        If there is no virtual hosting, return None
        """
        try:            
            root_path = self.context.REQUEST['VirtualRootPhysicalPath']
        except (AttributeError, KeyError), err:
            root_path =  None
        
        return root_path    

    def getVirtualHostKey(self):
        """ Get a key for the virtual host root.
    
        If there is no virtual hosting, return None.
        """
        # See also OFS/Traversable.py, line 31
        request = self.context.REQUEST
        return (request['SERVER_URL'], tuple(request._script))

    def getVirtualRoot(self):
        """ Get the virtual host root object.
        """
        root_path = self.getVirtualRootPhysicalPath()
        if root_path is None:
            return None
    
        return self.context.restrictedTraverse(root_path, None)

    def containsVirtualRoot(self):
        """ Return true if object contains the current virtual host root.
        """
        root_path = self.getVirtualRootPhysicalPath()
        if root_path is None:
            return 0
        object_path = self.context.getPhysicalPath()
        return pathContains(object_path, root_path)

def getVirtualHostingAdapter(context):
    return VirtualHostingAdapter(context).__of__(context)
    
def pathContains(path1, path2):
    """ 
    """
    return path2[:len(path1)] == path1
    

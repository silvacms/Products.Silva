# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: virtualhosting.py,v 1.2 2003/11/03 18:23:24 jw Exp $
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
        return self.getVirtualRootPhysicalPath()

    def getVirtualRoot(self):
        """ Get the virtual host root object.
        """
        root_path = self.getVirtualRootPhysicalPath()
        if root_path is None:
            return None
    
        try:
            root = self.context.restrictedTraverse(root_path)
        except (AttributeError, KeyError), err:
            root =  None
        
        return root

    def containsVirtualRoot(self):
        """ Return true if object points to an object within
        the context of a virtual host. False otherwise.
        """
        root_path = self.getVirtualRootPhysicalPath()
        if root_path is None:
            return 1
        object_path = self.context.getPhysicalPath()
        return pathContains(object_path, root_path)

def getVirtualHostingAdapter(context):
    return VirtualHostingAdapter(context).__of__(context)
    
def pathContains(path1, path2):
    """ 
    """
    return path2[:len(path1)] == path1
    
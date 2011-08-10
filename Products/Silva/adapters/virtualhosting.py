# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
#

from five import grok
from silva.core.interfaces import IVirtualHosting, ISilvaObject

# XXX should be a view ...

class VirtualHostingAdapter(grok.Adapter):
    """ Virtual Hosting adapter
    """

    grok.implements(IVirtualHosting)
    grok.context(ISilvaObject)

    def getVirtualRootPhysicalPath(self):
        """ Get the physical path of the object being the
        virtual host root.

        If there is no virtual hosting, return None
        """
        try:
            root_path = self.context.REQUEST['VirtualRootPhysicalPath']
        except (AttributeError, KeyError):
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

    def getSilvaOrVirtualRoot(self):
        """ Get either the virtual host root object, or the silva root.
        """
        root = self.getVirtualRoot()
        if root is None:
            return self.context.get_root()
        return root

    def containsVirtualRoot(self):
        """ Return true if object contains the current virtual host root.
        """
        root_path = self.getVirtualRootPhysicalPath()
        if root_path is None:
            return 0
        object_path = self.context.getPhysicalPath()
        return pathContains(object_path, root_path)

def getVirtualHostingAdapter(context):
    return IVirtualHosting(context)

def pathContains(path1, path2):
    """
    """
    return path2[:len(path1)] == path1


# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# Python
# Zope
import Globals
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo, allow_module
# Silva
from Products.Silva import interfaces
from Products.Silva import SilvaPermissions
from Products.Silva.adapters import adapter

from zope.interface import implements

class Haunted(adapter.Adapter):
    """Adapted content for retrieving the 'iterator' of haunting 
    objects (Ghosts).
    """
    
    implements(interfaces.IHaunted)
    
    security = ClassSecurityInfo()
    
    def __init__(self, context):
        adapter.Adapter.__init__(self, context)
        self.catalog = context.service_catalog

    def getHaunting(self):
        query = {
            'meta_type':  'Silva Ghost Version',
            'haunted_path': (self.context.getPhysicalPath(),),
            'version_status': 'public'}
        brains = self.catalog(query)
        for b in brains:
            yield b.getObject().get_silva_object()

class HauntedGhost(Haunted):
    """Adapted content for retrieving the 'iterator' of haunting 
    objects (Ghosts).
    """
    
    implements(interfaces.IHaunted)
    
    security = ClassSecurityInfo()
    
    def getHaunting(self):
        # Nothing to look for - Ghost cannot be haunted. Don't yield anything
        # XXX how to not yield anything??
        for b in []:
            yield None
            
# XXX Security declaration commented for the moment, as this adapter
# is not yet used by the view-layer.

#Globals.InitializeClass(Haunted)

#Globals.InitializeClass(HauntedGhost)

#allow_module('Products.Silva.adapters.haunted')

#__allow_access_to_unprotected_subobjects__ = True
    
#module_security = ModuleSecurityInfo('Products.Silva.adapters.haunted')
    
#module_security.declareProtected(
#    SilvaPermissions.ApproveSilvaContent, 'getHaunted')

def getHaunted(context):
    # XXX do we want to support container types too for this adapter?
    if interfaces.IGhost.providedBy(context):
        # It's a Ghost, return HauntedGhost adapter
        return HauntedGhost(context).__of__(context)
    if interfaces.IContent.providedBy(context):
        # If it is 'normal' content, we supply the Haunted adapter for it
        return Haunted(context).__of__(context)
    return None


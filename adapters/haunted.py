# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# Python
# Zope
import Globals
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo, allow_module
# Silva
from Products.Silva import interfaces
from Products.Silva import SilvaPermissions
from Products.Silva.adapters import adapter

class Haunted(adapter.Adapter):
    """Adapted content for retrieving the 'iterator' of haunting 
    objects (Ghosts).
    """
    
    __implements__ = (interfaces.IHaunted, )
    
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

Globals.InitializeClass(Haunted)

# Jumping through security hoops to get the adapter
# somewhat accessible to Python scripts

# Security declaration commented for the moment, as this adapter
# is not yet used by the view-layer.
#allow_module('Products.Silva.adapters.haunted')

#__allow_access_to_unprotected_subobjects__ = True
    
#module_security = ModuleSecurityInfo('Products.Silva.adapters.haunted')
    
#module_security.declareProtected(
#    SilvaPermissions.ApproveSilvaContent, 'getHaunted')

def getHaunted(context):
    if interfaces.IContainer.isImplementedBy(context):
        return Haunted(context).__of__(context)
    if interfaces.IContent.isImplementedBy(context):
        return Haunted(context).__of__(context)
    return None

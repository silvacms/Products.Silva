# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from grokcore import component

from Products.Silva import interfaces

class Haunted(component.Adapter):
    """Adapted content for retrieving the 'iterator' of haunting 
    objects (Ghosts).
    """
    component.context(interfaces.IContent)
    component.implements(interfaces.IHaunted)
    
    def __init__(self, context):
        self.context = context

    def getHaunting(self):
        catalog = self.context.service_catalog
        query = {
            'meta_type':  'Silva Ghost Version',
            'haunted_path': (self.context.getPhysicalPath(),),
            'version_status': 'public'}
        brains = catalog(query)
        for b in brains:
            yield b.getObject().get_silva_object()

class HauntedGhost(Haunted):
    """Adapted content for retrieving the 'iterator' of haunting 
    objects (Ghosts).
    """
    component.context(interfaces.IGhost)
    
    def getHaunting(self):
        # Nothing to look for - Ghost cannot be haunted. Don't yield anything
        # XXX how to not yield anything??
        for b in []:
            yield None


# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core import interfaces

class Haunted(grok.Adapter):
    """Adapted content for retrieving the 'iterator' of haunting 
    objects (Ghosts).
    """

    grok.implements(interfaces.IHaunted)
    grok.context(interfaces.IContent)
    
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
    grok.context(interfaces.IGhost)
    
    def getHaunting(self):
        # Nothing to look for - Ghost cannot be haunted. Don't yield anything
        # XXX how to not yield anything??
        if None:
            yield None


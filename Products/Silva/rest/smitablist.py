from infrae.rest import REST
from five import grok

import Acquisition 

from Products.Silva.interfaces import (ISilvaObject, 
                                       IVersionedContent, )

#                                       IVersionedAsset)

#in Silva 2.1, grok views STILL need to be zope 2 - acquisition
# enabled (i.e. inherit from Acquisition.Implicit
#XXXaa still needed in 2.3?
class SMITabList(REST, Acquisition.Implicit):
    """REST API to retrieve a JSON-formatted list of
       this silva object's tabs (name, id)
    """
    grok.name('smi-tab-list')
    grok.context(ISilvaObject)
    grok.require('silva.ReadSilvaContent')
    
    def GET(self):
        """Return the list of this object's tabs (name, id)"""
        sv = self.context.service_view_registry
        meta_type = self.context.meta_type
        view = sv.get_view('edit', meta_type)
        
        # remove all but the name and id
        tabs = [ t[:2] for t in view.get_tabs() ]
        return self.json_response(tabs)
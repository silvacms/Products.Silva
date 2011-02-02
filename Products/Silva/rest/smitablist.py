from zope.interface import alsoProvides
from five import grok
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider

import Acquisition 

from infrae.rest import REST
from silva.core.interfaces import ISilvaObject
from silva.core.smi.interfaces import ISMILayer

class SMITabList(REST):
    """REST API to retrieve a JSON-formatted list of
       this silva object's (context) tab info (name, id)
    """
    grok.name('smitablist.get_tabs')
    grok.context(ISilvaObject)
    grok.require('silva.ReadSilvaContent')
    
    def GET(self):
        """Return the list of this object's tabs (name, id)"""
        
        #the tabs are viewlets on the `smimenutabs` content provider.
        # to get to the viewlets, request needs to provide ISMILayer,
        # then need to get the edit tab (any tab would do),
        # then get the content provider
        # update() will set up the viewlets
        alsoProvides(self.request, ISMILayer)
        view = getMultiAdapter((self.context, self.request),
                               name="tab_edit_extra")
        menutabs = getMultiAdapter((self.context, self.request, view),
                                   name="smimenutabs")
        menutabs.update()
        tabs = []
        for tab in menutabs.viewlets:
            tabs.append([tab.name,tab.path])
        return self.json_response(tabs)
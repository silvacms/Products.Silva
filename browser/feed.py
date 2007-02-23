import Globals
from zope.interface import implements
from Products.Silva.adapters import adapter
from Products.Silva.interfaces import IFeed, IFeedItem, IContainer, IDocument

class ContainerFeedAdapter(adapter.Adapter):
    """Adapter for Silva container like objects to get their RSS or Atom feed 
    representation."""

    implements(IFeed)

    def atom(self, items=0):
        return None
    
    def rss(self, items=0):
        return None

def getFeedAdapter(context):
    if IContainer.implementedBy(context):
        return ContainerFeedAdapter(context).__of__(context)
    return None
    
class DocumentFeedItemAdapter(adapter.Adapter):
    """Adapter for Silva objects to get their RSS or Atom feed Item 
    representation."""

    implements(IFeedItem)

    def atomFeedItem(self):
        return None

    def rssFeedItem(self):
        return None
    
Globals.InitializeClass(FeedItemAdapter)

def getFeedItemAdapter(context):
    if IDocument.implementedBy(context):
        return DocumentFeedItemAdapter(context).__of__(context)
    return None

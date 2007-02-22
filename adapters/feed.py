import Globals
from zope.interface import implements
from Products.Silva.adapters import adapter
from Products.Silva.interfaces import IFeed, IFeedItem, IContainer, IDocument

class ContainerFeedAdapter(adapter.Adapter):
    """Adapter for Silva container like objects to get their RSS or Atom feed 
    representation."""

    implements(IFeed)

    def getFeed(self, format='atom', items=0):
        if format == 'atom':
            return self.getAtomFeed(items)
        return self.getRSSFeed(items)
    
    def getAtomFeed(self, items=0):
        return None
    
    def getRSSFeed(self, items=0):
        return None

def getFeedAdapter(context):
    if IContainer.implementedBy(context):
        return ContainerFeedAdapter(context).__of__(context)
    return None
    
class DocumentFeedItemAdapter(adapter.Adapter):
    """Adapter for Silva objects to get their RSS or Atom feed Item 
    representation."""

    implements(IFeedItem)

    def getFeedItem(self, format='atom'):
        if format == 'atom':
            return self.getAtomFeedItem()
        return self.getRSSFeedItem()

    def getAtomFeedItem(self):
        return None

    def getRSSFeedItem(self):
        return None
    
Globals.InitializeClass(FeedItemAdapter)

def getFeedItemAdapter(context):
    if IDocument.implementedBy(context):
        return DocumentFeedItemAdapter(context).__of__(context)
    return None

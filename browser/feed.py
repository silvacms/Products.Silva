import Globals
from zope import component
from zope.interface import implements
from Products.Silva.interfaces import IContainer
from Products.Silva.adapters.interfaces import IFeedEntry
from AccessControl import getSecurityManager
from Products.Five import BrowserView

class Data:
    def __init__(self, id, url):
        self.id = id
        self.title = ''
        self.description = ''
        self.url = url
        self.authors = []
        self.date_updated = None
        self.entries = []
        
class Entry:
    def __init__(self, id, url):
        self.id = id
        self.title = ''
        self.description = ''
        self.url = url
        self.authors = []
        self.date_updated = None
        self.date_published = None
        self.keywords = []

class ContainerFeedView(BrowserView):
    """Base class for feed representation."""

    def get_data(self):
        """ prepare the data needed by a feed
        """
        feed = []
        context = self.context
        for item in context.get_ordered_publishables():
            
            entry = IFeedEntry(item, None)
            if not entry is None:
                feed.append(entry)
        
        return {
            'id': 'id',
            'title': 'title',
            'description': 'description',
            'url': 'url',
            'authors': ['author1', 'author2'],
            'date_updated': '2007-02-23T19:12:12ZCET',
            'entries': feed 
            }

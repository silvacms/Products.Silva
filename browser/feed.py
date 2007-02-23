import Globals
from zope.interface import implements
from Products.Silva.interfaces import IContainer
from AccessControl import getSecurityManager
from Products.Five import BrowserView

class FeedView(BrowserView):
    """Base class for feed representation."""

    def get_data(self):
        """ prepare the data needed by a feed
        """
        return {
            'id': 'id',
            'title': 'title',
            'description': 'description',
            'url': 'url',
            'authors': ['author1', 'author2'],
            'date_updated': '2007-02-23T19:12:12ZCET',
            'entries': [
                {
                    'title': 'title',
                    'url': 'url',
                    'id': 'id1',
                    'date_published': '2007-02-23T18:12:12ZCET',
                    'date_updated': '2007-02-23T18:12:12ZCET',
                    'authors': ['author1', 'author2'],
                    'keywords': ['cool', 'feeds'],
                    'description': 'testing<br /><strong>1, 2</strong>'
                    },
                {
                    'title': 'title',
                    'url': 'url',
                    'id': 'id2',
                    'date_published': '2007-02-23T18:12:12ZCET',
                    'date_updated': '2007-02-23T18:12:12ZCET',
                    'authors': ['author1', 'author2'],
                    'keywords': ['cool', 'feeds'],
                    'description': 'testing<br /><strong>1, 2</strong>'
                    },
                {
                    'title': 'title',
                    'url': 'url',
                    'id': 'id4',
                    'date_published': '2007-02-23T19:12:12ZCET',
                    'date_updated': '2007-02-23T19:12:12ZCET',
                    'authors': ['author1', 'author2'],
                    'keywords': ['cool', 'feeds'],
                    'description': 'testing<br /><strong>1, 2</strong>'
                    },
                {
                    'title': 'title',
                    'url': 'url',
                    'id': 'id3',
                    'date_published': '2007-02-23T18:12:12ZCET',
                    'date_updated': '2007-02-23T18:12:12ZCET',
                    'authors': ['author1', 'author2'],
                    'keywords': ['cool', 'feeds'],
                    'description': 'testing<br /><strong>1, 2</strong>'
                    },],
            }

#class AtomView(FeedView):
#    """View on Silva containers to get their atom feed representation."""

#    def render(self, items=0):
#        return None


#class RssView(FeedView):
#    """View on Silva containers to get their rss feed representation."""

#    def render(self, items=0):
#        return None
    

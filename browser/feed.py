import Globals
from zope.interface import implements
from Products.Silva.interfaces import IContainer, IDocument
from AccessControl import getSecurityManager
from Products.Five import BrowserView

class AtomView(BrowserView):
    """View on Silva containers to get their atom feed representation."""

    def render(self, items=0):
        return None


class RssView(BrowserView):
    """View on Silva containers to get their rss feed representation."""

    def render(self, items=0):
        return None
    

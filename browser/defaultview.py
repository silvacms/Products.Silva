from zope import component
from Products.Five import BrowserView

class Legacy(BrowserView):
    def __call__(self):
        return getattr(self.context, 'index_html')()

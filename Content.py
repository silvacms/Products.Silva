import Interfaces
from SilvaObject import SilvaObject
from Publishable import Publishable

class Content(SilvaObject, Publishable):
    __implements__ = Interfaces.Content
    
    def is_default(self):
        return self.id == 'default'
    
    def get_content(self):
        """Get the content. Can be used with acquisition to get
        the 'nearest' content."""
        return self.aq_inner

    def content_url(self):
        """Get content URL."""
        return self.absolute_url()

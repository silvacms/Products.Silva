import Interfaces
from SilvaObject import SilvaObject
from Publishable import Publishable

class Content(SilvaObject, Publishable):
    __implements__ = Interfaces.Content
    
    def is_default(self):
        return self.id == 'default'
    

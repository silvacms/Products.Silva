import Interfaces
from Publishable import Publishable

class Content(Publishable):
    __implements__ = Interfaces.Content
    
    def is_default(self):
        return self.id == 'default'
    

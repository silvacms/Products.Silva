import Interfaces
from SilvaObject import SilvaObject

class Publishable(SilvaObject):
    __implements__ = Interfaces.Publishable

    _active_flag = 1
    
    def activate(self):
        if self._active_flag:
            return
        self._active_flag = 1
        self.get_folder()._refresh_ordered_ids(self)
  
    def deactivate(self):
        if not self._active_flag:
            return
        self._active_flag = 0
        self.get_folder()._refresh_ordered_ids(self)
        
    # ACCESSORS
    def is_active(self):
        return self._active_flag

    def is_published(self):
        raise NotImplementedError
    

import Interfaces

class Publishable:
    __implements__ = Interfaces.Publishable

    _active_flag = 1
    
    def activate(self):
        if self._active_flag:
            return
        # should make publishable active before we can add it
        self._active_flag = 1
        self.get_folder()._add_silva_object(self)
  
    def deactivate(self):
        if not self._active_flag:
            return
        self.get_folder()._remove_silva_object(self)
        # can only deactivate after removing it from list
        self._active_flag = 0
        
    # ACCESSORS
    def is_active(self):
        return self._active_flag

    def is_published(self):
        raise NotImplementedError
    

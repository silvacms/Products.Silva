import Interfaces

class Publishable:
    __implements__ = Interfaces.Publishable

    _active_flag = 1

    # MANIPULATORS
    def manage_afterAdd(self, item, container):
        #self.inheritedAttribute('manage_afterAdd')(self, item, container)
        container._add_ordered_publishable(item)
        
    def manage_beforeDelete(self, item, container):
        #self.inheritedAttribute('manage_beforeDelete')(self, item, container)
        container._remove_ordered_publishable(item)

    def activate(self):
        self._active_flag = 1
        self.get_folder._add_ordered_publishable(self)
  
    def deactivate(self):
        self._active_flag = 0
        self.get_folder()._remove_ordered_publishable(self)
        
    # ACCESSORS
    def is_active(self):
        return self._active_flag

    def is_published(self):
        raise NotImplementedError
    

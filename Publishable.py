import Interfaces
from SilvaObject import SilvaObject

class Publishable(SilvaObject):
    __implements__ = Interfaces.Publishable

    _active_flag = 1
    
    def activate(self):
        if not self.can_activate():
            return
        self._active_flag = 1
        self.get_folder()._refresh_ordered_ids(self)
  
    def deactivate(self):
        if not self.can_deactivate():
            return
        if Interfaces.Versioning.isImplementedBy(self):
            # if we want to deactivate an approved version, revoke
            # approval first
            if self.is_version_approved():
                self.unapprove_version() 
        self._active_flag = 0
        self.get_folder()._refresh_ordered_ids(self)
        
    # ACCESSORS

    def is_active(self):
        return self._active_flag

    def can_activate(self):
        if self._active_flag:
            return 0
        else:
            return 1
    
    def can_deactivate(self):
        if not self._active_flag:
            return 0
        if Interfaces.Versioning.isImplementedBy(self):
            # can't deactivate something with a published version
            if self.is_published():
                return 0
        return 1
    
    def is_published(self):
        if Interfaces.Versioning.isImplementedBy(self):
            return self.is_version_published()
        else:
            return 0
    
    def can_approve(self):
        """Return true if we can approve version.
        """
        return self.is_active()

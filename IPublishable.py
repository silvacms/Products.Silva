# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
import Interface

class IPublishable(Interface.Base):
    # MANIPULATORS
    def activate():
        """Make this publishable item active.
        """
        pass

    def deactivate():
        """Deactivate publishable item.
        """
        pass
    
    # ACCESSORS
    def is_published():
        """Return true if this object is visible to the public.
        PUBLIC
        """
        pass

    def is_approved():
        """Return true if this object is versioned or contains
        versioned content that is approved.
        """
        pass
    
    def is_active():
        """Returns true if this object is actually active and
        in the table of contents.
        PUBLIC
        """
        pass

    def can_activate():
        pass

    def can_deactivate():
        pass

from Interface import Interface

class IViewerSecurity(Interface):
    def setAcquired():
        """Set minimum viewer role restriction to acquire from above.
        """
        
    def setMinimumRole(role):
        """Set the minimum (viewer) role needed for view permission here.

        If role is Anonymous, viewer role restriction will be set to
        acquire from above.
        """

    def isAcquired():
        """Check whether minimum role is acquired.
        """
        
    def getMinimumRole():
        """Get the minimum role needed for view permission here.
        """

    def getMinimumRoleAbove():
        """Get the minimum role needed for view permission in parent.
        """

class ILockable(Interface):
    def createLock():
        """Create lock for context object.

        Return false if already locked, otherwise true.
        """

    def breakLock():
        """Break the lock.
        """

    def isLocked():
        """Check whether this object is locked by another user.
        """


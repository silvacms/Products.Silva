from Interface import Base

class IAccessManager(Base):
    """Mixin class for objects to request local roles on the object"""

    def request_role(self, userid, role):
        """Request a role on the current object and send an e-mail to the editor/chiefeditor/manager"""

    def allow_role(self, userid, role):
        """Allows the role and send an e-mail to the user"""

    def deny_role(self, userid, role):
        """Denies the role and send an e-mail to the user"""

        

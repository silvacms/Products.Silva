from Interface import Base

class IMember(Base):
    # ACCESSORS
    def userid():
        """Return unique id for member/username
        """

    def fullname():
        """Return full name
        """
        
    def email():
        """Return users's email address if known, None otherwise.
        """

    def is_approved():
        """Return true if this member is approved. Unapproved members
        may face restrictions on the Silva site.
        """

class IMemberService(Base):
    def find_members(search_string):
        """Return all users with a full name containing search string.
        """

    def is_user(userid):
        """Return true if userid is indeed a known user.
        """
        
    def get_member(userid):
        """Get member object for userid, or None if no such member object.
        """
    
class IMemberMessageService(Base):
    
    def send_message(from_memberid, to_memberid, subject, message):
        """Send a message from one member to another.
        """
        
    

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

    def departments():
        """Return list of departments user is in, or None if no such information.
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

    def get_cached_member(userid):
        """Get memberobject which can be cached, or None if no such memberobject.
        """

    def allow_subscription():
        """Return true if subscription is allowed, false if not
        """

    def get_subscription_url():
        """Returns the url of the subscription form
        """
    
# there is also expected to be a 'Members' object that is traversable
# to a Member object. Users can then modify information in the member
# object (if they have the permissions to do so, but the user associated
# with the member should do so)

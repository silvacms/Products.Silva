# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
import Interface
        
class IVersion(Interface.Base):
    """Version of a versioned object
    """

    def version_status():
        """Returns the current status of this version (unapproved, approved,
        public, last closed of closed)
        """

    def object_path():
        """Returns the physical path of the object this is a version of
        """

    def version():
        """Returns the version-id
        """

    def object():
        """Returns the object this is a version of
        """

    def publication_datetime():
        """Returns the version's publication datetime
        """

    def expiration_datetime():
        """Returns the version's expiration datetime
        """

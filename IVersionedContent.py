# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $

from IVersioning import IVersioning
from IContent import IContent

class IVersionedContent(IVersioning, IContent):
    """This is a content object that is versioned. Presumed is that
    upon creation of the content object it is assigned a version id
    that is registered with the Versioning interface as the unapproved
    version.
    """
    
    # MANIPULATORS
    def create_copy():
        """Create a new copy of the public version. Automatically
        assign a new id for this copy and register this as the
        next version. If there is already a next version, this
        operation will fail.
        """
        pass

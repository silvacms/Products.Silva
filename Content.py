# Version: $Revision: 1.9 $
import Interfaces
from SilvaObject import SilvaObject
from Publishable import Publishable

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
import SilvaPermissions

class Content(SilvaObject, Publishable):

    security = ClassSecurityInfo()
    
    __implements__ = Interfaces.Content

    # use __init__ of SilvaObject
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                             'is_default')
    def is_default(self):
        return self.id == 'index'

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_content')
    def get_content(self):
        """Get the content. Can be used with acquisition to get
        the 'nearest' content."""
        return self.aq_inner

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'content_url')
    def content_url(self):
        """Get content URL."""
        return self.absolute_url()

InitializeClass(Content)

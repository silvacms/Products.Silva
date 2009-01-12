# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
# Silva
from SilvaObject import SilvaObject
from Publishable import Publishable
import SilvaPermissions

from interfaces import IContent
from silva.core import conf as silvaconf

class Content(Publishable, SilvaObject):

    silvaconf.baseclass()

    security = ClassSecurityInfo()
    
    implements(IContent)

    object_type = 'content'

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


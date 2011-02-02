# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok

# Zope 2
from OFS.Folder import Folder as BaseFolder
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva.Publishable import PublishableBase
from Products.Silva import SilvaPermissions
from Products.Silva.Versionable import Versionable

from silva.core.interfaces import IVersionedAsset, IVersioning
from silva.core.services.interfaces import ICataloging, ICatalogingAttributes

class VersionedAsset(Versionable, PublishableBase, BaseFolder):
    security = ClassSecurityInfo()
    
    grok.implements(IVersionedAsset)
    grok.baseclass()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_content')
    def get_content(self):
        """Get the content. Can be used with acquisition to get
        the 'nearest' content.  This is copied from Content, so that assets
        can have a more similar api (esp. for versioned assets)."""
        return self.aq_inner
    
    # unimplemented IAsset methods.
    def update_quota(self):
        raise NotImplementedError

    def reset_quota(self):
        raise NotImplementedError
    
    def get_filename(self):
        raise NotImplementedError

    def get_file_size(self):
        raise NotImplementedError

    def get_mime_type(self):
        raise NotImplementedError
    # end unimplemented IAsset methods.
    
    #The following are copied from Publishable.  VersionedAsset
    # is a publishable, but cannot implement IPublishable
    # (or the asset will appear both above and below the line
    # in the container edit screen
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_published')
    def is_published(self):
        if IVersioning.providedBy(self):
            return self.is_version_published()
        else:
            return 1

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_approved')
    def is_approved(self):
        if IVersioning.providedBy(self):
            return self.is_version_approved()
        else:
            # never be approved if there is no versioning
            return 0

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_real_container')
    def get_real_container(self):
        """Get the container, even if we're a container.

        If we're the root object, returns None.
        
        Can be used with acquisition to get the 'nearest' container.
        """
        return self.get_container()    
    
InitializeClass(VersionedAsset)

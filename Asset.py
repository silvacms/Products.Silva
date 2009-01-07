# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.17 $
# Zope
from zope.interface import implements

from Globals import InitializeClass
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
import zLOG

# Silva
from SilvaObject import SilvaObject
import SilvaPermissions


from interfaces import IAsset

class Asset(CatalogPathAware, SilvaObject, SimpleItem.SimpleItem):
    implements(IAsset)

    security = ClassSecurityInfo()

    default_catalog = 'service_catalog'

    object_type = 'asset'
    _old_size = 0               # Old size of the object.

    # MANIPULATORS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_title')
    def set_title(self, title):
        """Set the title of the silva object.
        """
        # FIXME: Ugh. I get unicode from formulator but this will not validate
        # when using the metadata system. So first make it into utf-8 again..
        title = title.encode('utf-8')
        binding = self.service_metadata.getMetadata(self)
        binding.setValues(
            'silva-content', {'maintitle': title}, reindex=1)
        self.reindex_object()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'update_quota')
    def update_quota(self):
        if not self.service_extensions.get_quota_subsystem_status():
            return

        new_size = self.get_file_size()
        delta = new_size - self._old_size
        self.aq_parent.update_quota(delta)
        self._old_size = new_size

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'reset_quota')
    def reset_quota(self):
        self._old_size = self.get_file_size()
        return self._old_size

    # ACCESSORS

    def is_deletable(self):
        """assets are deletable

            NOTE: once there is reference management those should only be
            deletable if not referenced
        """
        return 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_navigation_links')
    def get_navigation_links(self):
        """
        Create a dictionary with top, up, first, previous, next, last links.
        
        This can be used by Mozilla in the accessibility toolbar.
        """
        return {}

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'version_status')
    def version_status(self):
        return 'public'

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                            'fulltext')
    def fulltext(self):
        fulltextlist = [self.id, self.get_title()]
        return fulltextlist

    def get_filename(self):
        raise NotImplementedError

    def get_file_size(self):
        raise NotImplementedError

    def get_mime_type(self):
        raise NotImplementedError
        

InitializeClass(Asset)


def asset_moved_update_quota(obj, event):
    if obj != event.object:
        return

    if event.newParent is event.oldParent: # For rename event, we
                                           # don't need to do
                                           # something.
        return

    context = event.newParent or event.oldParent
    if not context.service_extensions.get_quota_subsystem_status():
        return

    try:
        size = obj.get_file_size()
    except (AttributeError, NotImplementedError): # Well, not all
                                                  # asset respect its
                                                  # interface.
        path = '/'.join(obj.getPhysicalPath())
        klass = str(obj.__class__)
        zLOG.LOG('Silva quota', zLOG.WARNING, 
                 'bad asset object %s - %s' % (path, klass))
        return
    if not size:
        return
    if event.oldParent:
        event.oldParent.update_quota(-size)
    if event.newParent:
        event.newParent.update_quota(size)






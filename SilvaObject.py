import Interfaces

class SilvaObject:
    """Inherited by all Silva objects.
    """
    def __repr__(self):
        return "<%s instance %s>" % (self.meta_type, self.id)

    # MANIPULATORS
    def manage_afterAdd(self, item, container):
        #self.inheritedAttribute('manage_afterAdd')(self, item, container)
        container._refresh_ordered_ids(item)
        
    def manage_beforeDelete(self, item, container):
        #self.inheritedAttribute('manage_beforeDelete')(self, item, container)
        container._refresh_ordered_ids(item)

    # ACCESSORS
    
    def get_editable(self):
        """Get the editable version (may be object itself if no versioning).
        """
        return self

    def get_previewable(self):
        """Get the previewable version (may be the object itself if no
        versioning).
        """
        return self

    def get_viewable(self):
        """Get the publically viewable version (may be the object itself if
        no versioning).
        """
        return self

    # these help the UI that can't query interfaces directly
    def implements_publishable(self):
        return Interfaces.Publishable.isImplementedBy(self)
    
    def implements_asset(self):
        return Interfaces.Asset.isImplementedBy(self)

    def implements_content(self):
        return Interfaces.Content.isImplementedBy(self)

    def implements_container(self):
        return Interfaces.Container.isImplementedBy(self)

    def implements_versioning(self):
        return Interfaces.Versioning.isImplementedBy(self)

    def implements_versioned_content(self):
        return Interfaces.VersionedContent.isImplementedBy(self)

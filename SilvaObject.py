import Interfaces
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
import SilvaPermissions
from ViewRegistry import ViewAttribute
from DateTime import DateTime
from Security import Security
from StringIO import StringIO

class SilvaObject(Security):
    """Inherited by all Silva objects.
    """
    security = ClassSecurityInfo()

    # FIXME: this is for backward compatibility with old objects
    _title = "No title yet"
    _creation_datetime = None
    _modification_datetime = None
    
    # allow edit view on this object
    edit = ViewAttribute('edit')

    def __init__(self, id, title):
        self.id = id
        self._title = title
        self._creation_datetime = self._modification_datetime = DateTime()
        
    def __repr__(self):
        return "<%s instance %s>" % (self.meta_type, self.id)

    # MANIPULATORS
    def manage_afterAdd(self, item, container):
        container._add_ordered_id(item)
        
    def manage_beforeDelete(self, item, container):
        container._remove_ordered_id(item)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        """Set the title of the silva object.
        """
        self._title = title
        
    # ACCESSORS

    
    # create 'title' attribute for some Zope compatibility (still shouldn't set
    # titles in properties tab though)
    #security.declareProtected(SilvaPermissions.AccessContentsInformation,
    #                          'title')
    #def _get_title_helper(self):
    #    return self.get_title() # get_title() can be defined on subclass
    #title = ComputedAttribute(_zget_title_helper)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title')
    def get_title(self):
        """Get the title of the silva object.
        """
        return self._title

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_creation_datetime')
    def get_creation_datetime(self):
        """Return creation datetime."""
        return self._creation_datetime
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_modification_datetime')
    def get_modification_datetime(self):
        """Return modification datetime."""
        return self._modification_datetime

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_breadcrumbs')
    def get_breadcrumbs(self):
        """Get information used to display breadcrumbs. This is a
        list of items from the Silva Root.
        """
        result = []
        item = self
        while Interfaces.SilvaObject.isImplementedBy(item):
            result.append(item)
            item = item.aq_parent
        result.reverse()
        return result
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_editable')
    def get_editable(self):
        """Get the editable version (may be object itself if no versioning).
        """
        return self

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_previewable')
    def get_previewable(self):
        """Get the previewable version (may be the object itself if no
        versioning).
        """
        return self
    
    security.declareProtected(SilvaPermissions.View, 'get_viewable')
    def get_viewable(self):
        """Get the publically viewable version (may be the object itself if
        no versioning).
        """
        return self

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'preview')
    def preview(self):
        """Render this with the public view. If this is no previewable,
        should return something indicating this.
        """
        return self.service_view_registry.render_preview('public', self)

    security.declareProtected(SilvaPermissions.View, 'view')
    def view(self):
        """Render this with the public view. If there is no previewable,
        should return something indicating this.
        """
        return self.service_view_registry.render_view('public', self)
    
    # these help the UI that can't query interfaces directly

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'implements_publishable')
    def implements_publishable(self):
        return Interfaces.Publishable.isImplementedBy(self)
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'implements_asset')  
    def implements_asset(self):
        return Interfaces.Asset.isImplementedBy(self)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'implements_content')
    def implements_content(self):
        return Interfaces.Content.isImplementedBy(self)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'implements_container')
    def implements_container(self):
        return Interfaces.Container.isImplementedBy(self)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'implements_publication')
    def implements_publication(self):
        return Interfaces.Publication.isImplementedBy(self)
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'implements_versioning')
    def implements_versioning(self):
        return Interfaces.Versioning.isImplementedBy(self)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'implements_versioned_content')
    def implements_versioned_content(self):
        return Interfaces.VersionedContent.isImplementedBy(self)

    # HACK
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'activate_security_hack')
    def activate_security_hack(self):
        """This does nothing at all, except that calling this apparently
        as a side effect activates security on this object enough so you
        can check what roles a user has.
        """
        pass

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'get_xml')
    def get_xml(self):
        """Get XML for object and everything under it.
        """
        f = StringIO()
        self.to_xml(f)
        return f.getvalue()
    
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml') 
    def to_xml(self, f):
        """Handle unknown objects. (override in subclasses)
        """
        f.write('<unknown>%s</unknown>' % self.meta_type)
        
        
InitializeClass(SilvaObject)

# Zope
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
# Silva
from VersionedContent import VersionedContent
import Interfaces
# misc
from helpers import add_and_edit

class Ghost(VersionedContent):
    security = ClassSecurityInfo()

    meta_type = "Silva Ghost"

    __implements__ = Interfaces.VersionedContent
    
    def __init__(self, id):
        self.id = id
    
    def set_title(self):
        # FIXME: what to do here?
        pass
    
    def title(self):
        """Get title.
        """
        ghost_version = Ghost.inheritedAttribute('get_viewable')(self)
        if ghost_version is None:
            return ''
        return ghost_version._get_content().title()

    def get_creation_datetime(self):
        """Get creation datetime.
        """
        return DateTime.Datetime(2002, 1, 1, 12, 0)

    def get_modification_datetime(self):
        """Get modification datetime.
        """
        return DateTime.DateTime(2002, 1, 1, 12, 0)

    def get_previewable(self):
        ghost_version = Ghost.inheritedAttribute('get_previewable')(self)
        if ghost_version is None:
            return None
        return ghost_version._get_content().get_viewable()

    def get_viewable(self):
        ghost_version = Ghost.inheritedAttribute('get_viewable')(self)
        if ghost_version is None:
            return None
        return ghost_version._get_content().get_viewable()

Globals.InitializeClass(Ghost)

class GhostVersion(SimpleItem.Item):

    def __init__(self, id, content_url):
        self.id = id
        self._content_url = content_url

    def set_content_url(self, content_url):
        self._content_url = content_url

    def get_content_url(self):
        return self._content_url

    def _get_content(self):
        """Get the real content object.
        """
        # FIXME: what if we're pointing to something that cannot be viewed publically?
        if self._content_url is None:
            return None
        return self.getPhysicalRoot().unrestrictedTraverse(self._content_url)
        
manage_addGhostForm = PageTemplateFile("www/ghostAdd", globals(),
                                       __name__='manage_addGhostForm')

def manage_addGhost(self, id, content_url, REQUEST=None):
    """Add a Ghost."""
    object = Ghost(id)
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object.manage_addProduct['Silva'].manage_addGhostVersion('0', content_url)
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

# Zope
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
# XA
from TocSupport import TocSupport
# misc
from helpers import add_and_edit

class Ghost(TocSupport, SimpleItem.Item):
    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self._title = title
        self._document_url = None

    def _get_document(self):
        """Get the real document.
        """
        if self._document_url is None:
            return None
        return self.getPhysicalRoot().unrestrictedTraverse(self._document_url)
    
    def title(self):
        """Get title.
        """
        return self._title

    def get_creation_datetime(self):
        """Get creation datetime.
        """
        return DateTime.Datetime(2002, 1, 1, 12, 0)

    def get_modification_datetime(self):
        """Get modification datetime.
        """
        return DateTime.DateTime(2002, 1, 1, 12, 0)

    def view(self):
        """View document as HTML.
        """
        return self._get_document().view()

    def public(self):
        """Get version open to the public.
        """
        return self._get_document().view()

    def 
    
Globals.InitializeClass(Ghost)


manage_addGhostForm = PageTemplateFile("www/ghostAdd", globals(),
                                       __name__='manage_addGhostForm')

def manage_addGhost(self, id, title, REQUEST=None):
    """Add a Ghost."""
    object = Ghost(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''

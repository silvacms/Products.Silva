# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.39.8.1 $
# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
# Silva interfaces
from IPublication import IPublication
# Silva
from Folder import Folder
import SilvaPermissions
# misc
from helpers import add_and_edit, getNewId

from Products.Silva.ImporterRegistry import get_importer, xml_import_helper, get_xml_id, get_xml_title
from Products.Silva.Metadata import export_metadata

icon="www/silvapublication.gif"

class Publication(Folder):
    """These containers function as the major organizing blocks of a 
       Silva site. Publications instill a threshold of view, showing
       only the contents of the current publication (keeping the overview
       screens manageable) and have configuration settings which, a.o.,
       determine which core and pluggable objects will be available. For
       complex publications, sub-publications can be nested.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Publication"

    __implements__ = IPublication

    _addables_allowed_in_publication = None
    
    # MANIPULATORS
    
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'set_silva_addables_allowed_in_publication')
    def set_silva_addables_allowed_in_publication(self, addables):
        self._addables_allowed_in_publication = addables
    
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_folder')
    def to_folder(self):
        """Publication becomes a folder instead.
        """
        self._to_folder_or_publication_helper(to_folder=1)
        
    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_publication')
    def get_publication(self):
        """Get publication. Can be used with acquisition to get
        'nearest' Silva publication.
        """
        return self.aq_inner
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_transparent')
    def is_transparent(self):
        return 0

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml')
    def to_xml(self, context):
        """Render object to XML.
        """
        f = context.f
        f.write('<silva_publication id="%s">' % self.id)
        self._to_xml_helper(context)
        export_metadata(self, context)
        f.write('</silva_publication>')

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_silva_addables_allowed_in_publication')
    def get_silva_addables_allowed_in_publication(self):
        current = self
        root = self.get_root()
        while 1:
            addables = current._addables_allowed_in_publication
            if addables is not None:
                return addables
            elif current == root:
                return self.get_silva_addables_all()
            current = current.aq_parent

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_silva_addables_acquired')
    def is_silva_addables_acquired(self):
        return self._addables_allowed_in_publication is None

InitializeClass(Publication)

manage_addPublicationForm = PageTemplateFile("www/publicationAdd", globals(),
                                             __name__='manage_addPublicationForm')

def manage_addPublication(self, id, title, create_default=1, REQUEST=None):
    """Add a Silva publication."""
    if not self.is_id_valid(id):
        return
    object = Publication(id)
    self._setObject(id, object)
    object = getattr(self, id)
    # add doc
    if create_default:
        object.manage_addProduct['Silva'].manage_addDocument('index', title)
    if hasattr(object,'index'):
        object.index.sec_update_last_author_info()
    add_and_edit(self, id, REQUEST)
    return ''

def xml_import_handler(object, node):
    id = get_xml_id(node)
    title = get_xml_title(node)
    
    used_ids = object.objectIds()
    while id in used_ids:
        id = getNewId(id)
        
    object.manage_addProduct['Silva'].manage_addPublication(id, title, 0)
    
    newpub = getattr(object, id)
    for child in node.childNodes:
        if get_importer(child.nodeName):
            xml_import_helper(newpub, child)
        elif child.nodeName != u'title' and hasattr(newpub, 'set_%s' % child.nodeName) and child.childNodes[0].nodeValue:
            getattr(newpub, 'set_%s' % child.nodeName)(child.childNodes[0].nodeValue)
    return newpub

# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
# Zope
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
# Silva interfaces
from Products.Silva.IVersionedContent import IVersionedContent
# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.EditorSupportNested import EditorSupport
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import Version
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva.helpers import add_and_edit, translateCdata
# misc
from cgi import escape

class CatalogedDemoObject(CatalogedVersionedContent, EditorSupport):
    """Silva CatalogedDemoObject.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Cataloged DemoObject"

    __implements__ = IVersionedContent
       
    def __init__(self, id, title):
        """The constructor, does not do much in this case (just maps to
        the constructor of the parent).
        """
        CatalogedDemoObject.inheritedAttribute('__init__')(self, id, title)
    
InitializeClass(CatalogedDemoObject)

class CatalogedDemoObjectVersion(CatalogPathAware, Version):
    """Silva CatalogedDemoObject version.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Cataloged DemoObject Version"

    default_catalog = 'service_catalog'
    
    _is_cataloged = 1
    
    def __init__(self, id, title):
        """Set id and initialize the ParsedXML tree.
        """
        self.id = id
        self._info = ''
        self._number = 0
        self._date = None
        self.content = ParsedXML('content', '<doc></doc>')
        
    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_demo_data')
    def set_demo_data(self, info, number, date):
        """Set the info for this version.
        """
        self._info = info
        self._number = number
        self._date = date
        self.reindex_object()
        
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'info')
    def info(self):
        """Get the info for this version.
        """
        return self._info
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'number')
    def number(self):
        """Get the number for this version.
        """
        return self._number
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'date')
    def date(self):
        """Get the date for this version.
        """
        return self._date
    
InitializeClass(CatalogedDemoObjectVersion)

manage_addCatalogedDemoObjectForm = PageTemplateFile("www/catalogedDemoObjectAdd", globals(),
                                        __name__='manage_addCatalogedDemoObjectForm')

def manage_addCatalogedDemoObject(self, id, title, REQUEST=None):
    """Add a CatalogedDemoObject to the Silva-instance."""
    if not self.is_id_valid(id):
        return
    object = CatalogedDemoObject(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object._setObject('0', CatalogedDemoObjectVersion('0', 'demo-object dummy title'))
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addCatalogedDemoObjectVersionForm = PageTemplateFile("www/catalogedDemoObjectVersionAdd", globals(),
                                               __name__='manage_addCatalogedDemoObjectVersionForm')

def manage_addCatalogedDemoObjectVersion(self, id, title, REQUEST=None):
    """Add a CatalogedDemoObject version to the Silva-instance."""
    object = CatalogedDemoObjectVersion(id, title)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''

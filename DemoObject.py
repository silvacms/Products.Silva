# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.7 $
# Zope
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
# Silva interfaces
from IVersionedContent import IVersionedContent
# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.EditorSupport import EditorSupport
from Products.Silva.VersionedContent import VersionedContent
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva.helpers import add_and_edit, translateCdata
# misc
from cgi import escape

class DemoObject(VersionedContent, EditorSupport):
    """Silva DemoObject.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva DemoObject"

    __implements__ = IVersionedContent
       
    def __init__(self, id, title):
        """The constructor, does not do much in this case (just maps to
        the constructor of the parent).
        """
        DemoObject.inheritedAttribute('__init__')(self, id, title)
    
InitializeClass(DemoObject)

class DemoObjectVersion(SimpleItem.SimpleItem):
    """Silva DemoObject version.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva DemoObject Version"

    def __init__(self, id, title):
        """Set id and initialize the ParsedXML tree.
        """
        self.id = id
        self._info = ''
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
    
InitializeClass(DemoObjectVersion)

manage_addDemoObjectForm = PageTemplateFile("www/demoObjectAdd", globals(),
                                        __name__='manage_addDemoObjectForm')

def manage_addDemoObject(self, id, title, REQUEST=None):
    """Add a DemoObject to the Silva-instance."""
    if not self.is_id_valid(id):
        return
    object = DemoObject(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object._setObject('0', DemoObjectVersion('0', 'demo-object dummy title'))
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addDemoObjectVersionForm = PageTemplateFile("www/demoObjectVersionAdd", globals(),
                                               __name__='manage_addDemoObjectVersionForm')

def manage_addDemoObjectVersion(self, id, title, REQUEST=None):
    """Add a DemoObject version to the Silva-instance."""
    object = DemoObjectVersion(id, title)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''

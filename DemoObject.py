# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.14 $
# Zope
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
# Silva interfaces
from Products.Silva.IVersionedContent import IVersionedContent
# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import VersionedContent
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva.helpers import add_and_edit, translateCdata
# misc
from cgi import escape

from Products.Silva.ImporterRegistry import importer_registry, xml_import_helper, get_xml_id, get_xml_title
from Products.ParsedXML.ExtraDOM import writeStream

icon="www/silvageneric.gif"

class DemoObject(VersionedContent):
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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_xml')
    def to_xml(self, context):
        """Returns this object as XML"""
        f = context.f
        if context.last_version == 1:
            version_id = self.get_next_version()
            if version_id is None:
                version_id = self.get_public_version()
        else:
            version_id = self.get_public_version()

        if version_id is None:
            return

        version = getattr(self, version_id)
        f.write('<silva_demoobject id="%s">' % self.id)
        f.write('<title>%s</title>' % translateCdata(self.get_title()))
        f.write('<info>%s</info>' % version.info())
        f.write('<number>%s</number>' % version.number())
        f.write('<date>%s</date>' % version.date())
        version.content.documentElement.writeStream(f)
        f.write('</silva_demoobject>')

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
        self._number = 0
        self._date = DateTime()
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

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_info')
    def set_info(self, value):
        """Sets info"""
        self._info = value

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'number')
    def number(self):

        """Get the number for this version.
        """
        return self._number

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_number')
    def set_number(self, value):
        """Sets number"""
        self._number = value

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'date')
    def date(self):
        """Get the date for this version.
        """
        return self._date

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_date')
    def set_date(self, value):
        if type(value) != DateTime:
            value = DateTime(value)
        self._date = value

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

def xml_import_handler(object, node):
    id = get_xml_id(node)
    title = get_xml_title(node)
    object.manage_addProduct['Silva'].manage_addDemoObject(id, title)
    newdo = getattr(object, id)
    version = getattr(newdo, '0')
    for child in node.childNodes:
        if child.nodeName == u'doc':
            childxml = writeStream(child).getvalue().encode('utf8')
            version.content.manage_edit(childxml) # expects utf8
        elif hasattr(version, 'set_%s' % child.nodeName.encode('cp1252')) and child.childNodes[0].nodeValue:
            getattr(version, 'set_%s' % child.nodeName.encode('cp1252'))(child.childNodes[0].nodeValue.encode('cp1252'))


# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.28 $
# Python
from StringIO import StringIO
# Zope
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva import mangle
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva.helpers import add_and_edit, translateCdata
from Products.Silva.Version import CatalogedVersion
from Products.Silva.ImporterRegistry import importer_registry, \
                     xml_import_helper, get_xml_id, get_xml_title

from Products.Silva.Metadata import export_metadata
from Products.ParsedXML.ExtraDOM import writeStream

from interfaces import IVersionedContent, IVersion

icon="www/silvageneric.gif"

class DemoObject(CatalogedVersionedContent):
    """Developers can create 'pluggable' Silva objects,
       new content types which can be plugged into Silva. They can be 
       turned on and off per publication (same as Silva core objects). 
       The Silva DemoObject is provided as an example of a hybrid content 
       type, which mixes required fields with free flowing structured text.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva DemoObject"

    __implements__ = IVersionedContent
       
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
        version.to_xml(context)
        f.write('</silva_demoobject>')

InitializeClass(DemoObject)

class DemoObjectVersion(CatalogedVersion):
    """Silva DemoObject version.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva DemoObject Version"
    
    __implements__ = IVersion

    def __init__(self, id, title):
        """Set id and initialize the ParsedXML tree.
        """
        DemoObjectVersion.inheritedAttribute('__init__')(self, id, title)
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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Return the content of this object without any xml"""
        return '%s %s' % (self._flattenxml(self.content_xml()), self.info())
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'content_xml')
    def content_xml(self):
        """Returns the documentElement of the content's XML
        """
        s = StringIO()
        self.content.documentElement.writeStream(s)
        value = s.getvalue()
        s.close()
        return value

    def to_xml(self, context):
        f = context.f
        f.write('<title>%s</title>' % translateCdata(self.get_title()))
        self.content.documentElement.writeStream(f)
        f.write('<info>%s</info>' % translateCdata(self.info()))
        f.write('<number>%s</number>' % translateCdata(self.number()))
        f.write('<date>%s</date>' % self.date())
        export_metadata(self, context)

    def manage_afterClone(self, item):
        # XXX cut & paste from the DocumentVersion.manage_afterClone
        self.service_editor.clearCache(self.content)

    def _flattenxml(self, xmlinput):
        """Cuts out all the XML-tags, helper for fulltext (for content-objects)
        """
        # XXX this need to be fixed by using ZCTextIndex or the like
        return xmlinput
        
InitializeClass(DemoObjectVersion)

manage_addDemoObjectForm = PageTemplateFile("www/demoObjectAdd", globals(),
                                        __name__='manage_addDemoObjectForm')

def manage_addDemoObject(self, id, title, REQUEST=None):
    """Add a DemoObject to the Silva-instance."""
    if not mangle.Id(self, id).isValid():
        return
    object = DemoObject(id)
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object.manage_addProduct['Silva'].manage_addDemoObjectVersion('0', title)
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addDemoObjectVersionForm = PageTemplateFile("www/demoObjectVersionAdd",
                                    globals(), 
                                    __name__='manage_addDemoObjectVersionForm')

def manage_addDemoObjectVersion(self, id, title, REQUEST=None):
    """Add a DemoObject version to the Silva-instance."""
    version = DemoObjectVersion(id, title)
    self._setObject(id, version)

    version = self._getOb(id)
    version.set_title(title)

    add_and_edit(self, id, REQUEST)
    return ''

def xml_import_handler(object, node):
    id = get_xml_id(node)
    title = get_xml_title(node)
    object.manage_addProduct['Silva'].manage_addDemoObject(id, title)
    newdo = getattr(object, id)
    newdo.sec_update_last_author_info()
    version = getattr(newdo, '0')
    for child in node.childNodes:
        if child.nodeName == u'doc':
            childxml = writeStream(child).getvalue().encode('utf8')
            version.content.manage_edit(childxml) # expects utf8
        elif (hasattr(version, 'set_%s' % child.nodeName)
              and child.childNodes and child.childNodes[0].nodeValue):
            getattr(version, 'set_%s' % child.nodeName) \
                        (child.childNodes[0].nodeValue)

    return newdo

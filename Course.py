# Zope
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
import SilvaPermissions
# Silva
from VersionedContent import VersionedContent
import Interfaces
from Products.ParsedXML.ParsedXML import ParsedXML

# misc
from helpers import add_and_edit
from cgi import escape

class Course(VersionedContent):
    """Silva Course.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Course"

    __implements__ = Interfaces.VersionedContent
       
    def __init__(self, id, title):
        Course.inheritedAttribute('__init__')(self, id, title)
        
    # MANIPULATORS

    # FIXME -- do we want set_title like this?
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        """Set the title.
        """
        if self.is_default():
            # set the nearest container's title
            self.get_container().set_title(title)
        else:
            # set title of this document
            self._title = title

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'xml_url')
    def xml_url(self):
        """Get URL for xml data.
        """
        return self.absolute_url() + '/' + self.get_unapproved_version()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title')
    def get_title(self):
        """Get title. If we're the default document,
        we get title from our containing folder (or publication, etc).
        """
        if self.is_default():
            # get the nearest container's title
            return self.get_container().get_title()
        else:
            return self._title
                        
InitializeClass(Course)

class CourseVersion(SimpleItem.SimpleItem):
    """Silva Course version.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Course Version"
    
    def __init__(self, id):
        self.id = id
        self.title = id
        self._goal = ParsedXML(id, '<doc></doc>')
        self._content = ParsedXML(id, '<doc></doc>')
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_data')
    def set_data(self, dict):
        """Set the data dictionary.
        """
        self._data = dict
        
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_data')
    def get_data(self):
        """Get the data dictionary.
        """
        return self._data

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_goal')
    def get_goal(self):
        return self._goal

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_content')
    def get_content(self):
        return self._content
    
InitializeClass(CourseVersion)

manage_addCourseForm = PageTemplateFile("www/courseAdd", globals(),
                                        __name__='manage_addCourseForm')

def manage_addCourse(self, id, title, REQUEST=None):
    """Add a Course."""
    if not self.is_id_valid(id):
        return
    object = Course(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object._setObject('0', CourseVersion('0'))
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addCourseVersionForm = PageTemplateFile("www/courseversionAdd", globals(),
                                               __name__='manage_addCourseVersionForm')

def manage_addCourseVersion(self, id, REQUEST=None):
    """Add a Course version."""
    object = CourseVersion(id)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''

# Zope
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
import SilvaPermissions
# Silva
from EditorSupport import EditorSupport
from VersionedContent import VersionedContent
import Interfaces
from Products.ParsedXML.ParsedXML import ParsedXML

# misc
from helpers import add_and_edit, translateCdata
from cgi import escape

class Course(VersionedContent, EditorSupport):
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
        version = self.get_editable()
        if version is None:
            return
        version._data['course_title'] = title
        version._data = version._data
                
        #if self.is_default():
        #    # set the nearest container's title
        #    self.get_container().set_title(title)
        #else:
        #    # set title of this document
        #    self._title = title

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title')
    def get_title(self):
        """Get title. If we're the default document,
        we get title from our containing folder (or publication, etc).
        """
        version = self.get_previewable() or self.get_viewable()
        if version is None:
            return "Course has no title"
        return version.get_data()['course_title']
        #if self.is_default():
        #    # get the nearest container's title
        #    return self.get_container().get_title()
        #else:
        #    return self._title

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml')
    def to_xml(self, f):
        version_id = self.get_public_version()
        if version_id is None:
            return
        version = getattr(self, version_id)
        f.write('<silva_course id="%s">' % self.id)
        for key, value in version._data.items():
            f.write('<%s>%s</%s>' % (key, translateCdata(value), key))
        f.write('<content>')
        version.content.documentElement.writeStream(f)
        f.write('</content>')
        f.write('<goal>')
        version.content.documentElement.writeStream(f)
        f.write('</goal>')
        f.write('</silva_course>')

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'upgrade_xml')
    def upgrade_xml(self):
        """Upgrade xml.
        """
        title = self.get_title()
        if type(title) != type(u''):
            self.set_title(self.input_convert(title))
        # upgrade the public version, the last closed version, and the
        # next version, if they exist
        versions = [self.get_last_closed_version(),
                    self.get_public_version(),
                    self.get_next_version()]
        for version in versions:
            if version is None:
                continue
            course = getattr(self, version)
            self._upgrade_xml_helper(course.goal.documentElement)   
            self._upgrade_xml_helper(course.content.documentElement)
            data = course.get_data()
            for key, value in data.items():
                if type(value) != type(u''):
                    data[key] = self.input_convert(value)
            course.set_data(data)
            
InitializeClass(Course)

class CourseVersion(SimpleItem.SimpleItem):
    """Silva Course version.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Course Version"

    def __init__(self, id, title):
        self.id = id
        self.title = title 
        self._data = { 'course_title' : title}
        self.goal = ParsedXML('goal', '<doc></doc>')
        self.content = ParsedXML('content', '<doc></doc>')
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_data')
    def set_data(self, dict):
        """Set the data dictionary.
        """
        self._data = dict

    #def set_data_entry(self, name, value):
    #    self._data[name] = value
    #    self._data = self._data
        
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_data')
    def get_data(self):
        """Get the data dictionary.
        """
        return self._data


    
InitializeClass(CourseVersion)

manage_addCourseForm = PageTemplateFile("www/courseAdd", globals(),
                                        __name__='manage_addCourseForm')

def manage_addCourse(self, id, title, REQUEST=None):
    """Add a Course."""
    if not self.is_id_valid(id):
        return
    object = Course(id, 'course dummy title')
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object._setObject('0', CourseVersion('0', title))
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

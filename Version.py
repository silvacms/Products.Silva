from StringIO import StringIO

from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware

from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva.IVersion import IVersion
from Products.Silva import SilvaPermissions

class Version(SimpleItem):

    __implements__ = IVersion

    security = ClassSecurityInfo()

    object_type = 'versioned_content'

    def __init__(self, id, title=None):
        self.id = id
        self.content = ParsedXML('content', '<doc></doc>')

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'version_status')
    def version_status(self):
        """Returns the status of the current version
        Can be 'unapproved', 'approved', 'public', 'last_closed' or 'closed'
        """
        status = None
        unapproved_version = self.get_unapproved_version(0)
        approved_version = self.get_approved_version(0)
        public_version = self.get_public_version(0)
        previous_versions = self.get_previous_versions()
        if unapproved_version and unapproved_version == self.id:
            status = "unapproved"
        elif approved_version and approved_version == self.id:
            status = "approved"
        elif public_version and public_version == self.id:
            status = "public"
        else:
            if previous_versions and previous_versions[-1] == self.id:
                status = "last_closed"
            elif self.id in previous_versions:
                status = "closed"
            else:
                status = 'unapproved' # this is a completely new version not even registered with the machinery yet
                # raise ValueError, "Version %s not found in object %s" % (self.id, self.object().id)
        return status

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'object_path')
    def object_path(self):
        """Returns the physical path of the object (for identification-purposes)
        """
        return self.aq_inner.aq_parent.getPhysicalPath()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'version')
    def version(self):
        """Returns the version
        """
        return (self.id, self.publication_datetime(), self.expiration_datetime())

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'object')
    def object(self):
        """Returns the object this version belongs to
        """
        return self.aq_inner.aq_parent

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'publication_datetime')
    def publication_datetime(self):
        """Returns the publication_datetime of this version (if any)
        """
        status = self.version_status()
        if status == 'closed' or status == 'last_closed':
            return None
        else:
            return getattr(self, 'get_%s_version_publication_datetime' % status)(0)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'expiration_datetime')
    def expiration_datetime(self):
        """Returns the expiration_datetime of this version (if any)
        """
        status = self.version_status()
        if status == 'closed' or status == 'last_closed':
            return None
        else:
            return getattr(self, 'get_%s_version_expiration_datetime' % status)(0)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Return the content of this object without any xml"""
        content = self._flattenxml(self.content_xml())
        return content
        
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

    def _flattenxml(self, xmlinput):
        """Cuts out all the XML-tags, helper for fulltext (for content-objects)
        """
        # FIXME: should take care of CDATA-chunks as well...
        while 1:
            ltpos = xmlinput.find('<')
            gtpos = xmlinput.find('>')
            if ltpos > -1 and gtpos > -1:
                xmlinput = xmlinput.replace(xmlinput[ltpos:gtpos + 1], ' ')
            else:
                break
        return xmlinput

InitializeClass(Version)

# CatalogPathAware is the second inherited superclass and Version (which 
# inherits from SimpleItem) the first. This way Version's manage_* methods 
# override CatalogPathAware's, which is exactly what we want, since 
# cataloging is done by VersionedContent (a superclass of the container).
class CatalogedVersion(Version, CatalogPathAware):
    """Superclass for cataloged version objects"""
    default_catalog = 'service_catalog'

InitializeClass(CatalogedVersion)


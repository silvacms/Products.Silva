# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Silva
from VersionedContent import CatalogedVersionedContent
from Version import CatalogedVersion
import SilvaPermissions
from interfaces import IVersionedContent, IVersion
import mangle
from helpers import add_and_edit

class Link(CatalogedVersionedContent):
    security = ClassSecurityInfo()

    meta_type = "Silva Link"

    __implements__ = IVersionedContent

    def __init__(self, id):
        Link.inheritedAttribute('__init__')(self, id)
        self.id = id

InitializeClass(Link)

manage_addLinkForm = PageTemplateFile("www/linkAdd", globals(),
                                       __name__='manage_addLinkForm')
 
def manage_addLink(self, id, title, url, REQUEST=None):
    """Add a Link."""
    if not mangle.Id(self, id).isValid():
        return
    object = Link(id)
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object.manage_addProduct['Silva'].manage_addLinkVersion(
        '0', title, url)
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

class LinkVersion(CatalogedVersion):
    security = ClassSecurityInfo()
    
    meta_type = "Silva Link Version"

    __implements__ = IVersion

    def __init__(self, id, url):
        LinkVersion.inheritedAttribute('__init__')(self,
                                                   id, 'not the real title')
        self.set_url(url)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'get_url')
    def get_url(self):
        return self._url

    security.declareProtected(SilvaPermissions.View, 'redirect')
    def redirect(self, view_type='public'):
        request = self.REQUEST
        response = request.RESPONSE
       
        if (request['HTTP_USER_AGENT'].startswith('Mozilla/4.77') or
            request['HTTP_USER_AGENT'].find('Konqueror') > -1 or
            request['HTTP_USER_AGENT'].find('Opera') > -1):
            return ('<html><head><META HTTP-EQUIV="refresh" '
                    'CONTENT="0; URL=%s"></head><body bgcolor="#FFFFFF">'
                    '</body></html>') % self._url
        else:
            response.redirect(self._url)
            return None
        
    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'set_url')
    def set_url(self, url):
        if not url.startswith('http://'):
            url = 'http://' + url
        self._url = url

InitializeClass(LinkVersion)

manage_addLinkVersionForm = PageTemplateFile(
    "www/linkversionAdd", globals(),
    __name__='manage_addLinkVersionForm')
                                                                                
def manage_addLinkVersion(self, id, title, url, REQUEST=None):
    """Add a Link version."""
    object = LinkVersion(id, url)
    self._setObject(id, object)
    self._getOb(id).set_title(title)
    add_and_edit(self, id, REQUEST)
    return ''

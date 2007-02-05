# Copyright (c) 2003-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.13 $

from zope.interface import implements

# python
import re
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
from helpers import add_and_edit, translateCdata
from Products.Silva.ImporterRegistry import get_xml_id, get_xml_title
from Products.Silva.Metadata import export_metadata
from Products.Silva.i18n import translate as _

# XXX taken from SilvaDocument/mixedcontentsupport.py
URL_PATTERN = r'(((http|https|ftp|news)://([A-Za-z0-9%\-_]+(:[A-Za-z0-9%\-_]+)?@)?([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+)(:[0-9]+)?(/([A-Za-z0-9\-_\?!@#$%^&*/=\.]+[^\.\),;\|])?)?|(mailto:[A-Za-z0-9_\-\.]+@([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+))'
_url_match = re.compile(URL_PATTERN)

class Link(CatalogedVersionedContent):
    __doc__ = _("""A Silva Link makes it possible to include links to external
       sites &#8211; outside of Silva &#8211; in a Table of Contents. The
       content of a Link is simply a hyperlink, beginning with
       &#8220;http://....&#8221;, or https, ftp, news, and mailto.
    """)
    security = ClassSecurityInfo()

    meta_type = "Silva Link"

    implements(IVersionedContent)

    def __init__(self, id):
        Link.inheritedAttribute('__init__')(self, id)
        self.id = id

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'to_xml')
    def to_xml(self, context):
        """Render object to XML.
        """
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
        f.write('<silva_link id="%s">' % self.id)
        f.write('<title>%s</title>' % translateCdata(version.get_title()))
        f.write('<url>%s</url>' % translateCdata(version.get_url()))
        export_metadata(version, context)
        f.write('</silva_link>')

InitializeClass(Link)

class LinkVersion(CatalogedVersion):
    security = ClassSecurityInfo()
    
    meta_type = "Silva Link Version"

    implements(IVersion)

    _link_type = 'absolute'
    
    def __init__(self, id, url, link_type='absolute'):
        LinkVersion.inheritedAttribute('__init__')(self, id)
        self._link_type = link_type
        self.set_url(url)
        
    security.declareProtected(SilvaPermissions.View, 'get_url')
    def get_url(self):
        return self._url

    security.declareProtected(SilvaPermissions.View, 'redirect')
    def redirect(self, view_type='public'):
        request = self.REQUEST
        response = request.RESPONSE
        url = self._url
        if self._link_type == 'relative' and not request.get('ACTUAL_URL').endswith('/'):
            url = '%s/%s' %(request.get('ACTUAL_URL'), url)
        
        if (request['HTTP_USER_AGENT'].startswith('Mozilla/4.77') or
            request['HTTP_USER_AGENT'].find('Konqueror') > -1 or
            request['HTTP_USER_AGENT'].find('Opera') > -1):
            return ('<html><head><META HTTP-EQUIV="refresh" '
                    'CONTENT="0; URL=%s"></head><body bgcolor="#FFFFFF">'
                    '</body></html>') % url
        else:
            response.redirect(self._url)
            return ""
        
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'is_valid_url')
    def is_valid_url(self, url):
        if _url_match.match(url):
            return True
        return False
        
    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_url')
    def set_url(self, url):
        if self._link_type == 'absolute' and not self.is_valid_url(url):
            url = 'http://' + url
        self._url = url

InitializeClass(LinkVersion)

def xml_import_handler(object, node):
    id = get_xml_id(node)
    title = get_xml_title(node)
    url = ''
    for child in node.childNodes:
        if child.nodeName == u'url':
            url = child.childNodes[0].nodeValue;
   
    id = str(mangle.Id(object, id).unique())
    object.manage_addProduct['Silva'].manage_addLink(id, title, url)
    
    newdoc = getattr(object, id)
    newdoc.sec_update_last_author_info()
    
    return newdoc


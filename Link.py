# Copyright (c) 2003-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import re

from warnings import warn

# Zope 3
from zope.interface import implements

# Zope 2
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# Silva
from VersionedContent import CatalogedVersionedContent
from Version import CatalogedVersion
import SilvaPermissions
from interfaces import IVersionedContent, IVersion
import mangle
from helpers import translateCdata
from Products.Silva.ImporterRegistry import get_xml_id, get_xml_title
from Products.Silva.Metadata import export_metadata
from Products.Silva.i18n import translate as _

# XXX taken from SilvaDocument/mixedcontentsupport.py
URL_PATTERN = r'(((http|https|ftp|news)://([A-Za-z0-9%\-_]+(:[A-Za-z0-9%\-_]+)?@)?([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+)(:[0-9]+)?(/([A-Za-z0-9\-_\?!@#$%^&*/=\.]+[^\.\),;\|])?)?|(mailto:[A-Za-z0-9_\-\.]+@([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+))'
_url_match = re.compile(URL_PATTERN)

class Link(CatalogedVersionedContent):
    __doc__ = _("""A Silva Link makes it possible to create links that show up
    in navigation or a Table of Contents. The links can be absolute or relative.
    Absolute links go to external sites while relative links go to content
    within Silva. The Link can be a hyperlink, beginning with "http://...."
    (including https, ftp, news, and mailto) or a path to Silva content. If the
    path goes to Silva content which doesn't exist, 'http://' will be placed
    before the link. This allows you to paste "www.somesite.com" into the field.
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
        warn('Use silvaxml/xmlexport instead of to_xml.'
             ' to_xml will be removed in Silva 2.2.', 
             DeprecationWarning)
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

    security.declareProtected(SilvaPermissions.View, 'get_link_type')
    def get_link_type(self):
        return self._link_type

    security.declareProtected(SilvaPermissions.View, 'redirect')
    def redirect(self, view_type='public'):
        request = self.REQUEST
        response = request.RESPONSE
        if (request['HTTP_USER_AGENT'].startswith('Mozilla/4.77') or
            request['HTTP_USER_AGENT'].find('Opera') > -1):
            return ('<html><head><META HTTP-EQUIV="refresh" '
                    'CONTENT="0; URL=%s"></head><body bgcolor="#FFFFFF">'
                    '</body></html>') % self._url
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
        
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_link_type')
    def set_link_type(self, lt):
        if lt=='absolute':
            self._link_type = 'absolute'
        else:
            self._link_type = 'relative'

InitializeClass(LinkVersion)

def xml_import_handler(object, node):
    warn('Use silvaxml/xmlimport instead of import_handler', 
         DeprecationWarning)
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


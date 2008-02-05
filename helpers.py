# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.30 $
# Zope
from AccessControl import ModuleSecurityInfo
from zope.app.container.interfaces import (IObjectRemovedEvent,
                                           IObjectAddedEvent)
# Silva 
import SilvaPermissions
# python
import string, re, urllib
from cgi import escape

from interfaces import ISilvaObject, IVersioning, IContainer, IAsset

module_security =  ModuleSecurityInfo('Products.Silva.helpers')

def add_and_edit(self, id, REQUEST, screen='manage_main'):
    """Helper function to point to the object's management screen if
    'Add and Edit' button is pressed.
    id -- id of the object we just added
    """
    if REQUEST is None:
        return
    try:
        u = self.DestinationURL()
    except:
        u = REQUEST['URL1']
    if REQUEST.has_key('submit_edit'):
        u = "%s/%s" % (u, urllib.quote(id))
        REQUEST.RESPONSE.redirect(u+'/'+screen)
    else:
        REQUEST.RESPONSE.redirect(u+'/manage_main')

def unapprove_helper(object):
    """Unapprove object and anything unapprovable contained by it.
    """
    if IVersioning.providedBy(object):
        if object.is_version_approved():
            object.unapprove_version()
    if IContainer.providedBy(object):
        for item in object.get_ordered_publishables():
            unapprove_helper(item)
    
def unapprove_close_helper(object):
    """Unapprove/close object and anything unapprovable/closeable contained by it.
    """
    if IVersioning.providedBy(object):
        if object.is_version_approved():
            object.unapprove_version()
        if object.is_version_published():
            object.close_version()
    if IContainer.providedBy(object):
        default = object.get_default()
        if default:
            unapprove_close_helper(default)
        for item in object.get_ordered_publishables():
            unapprove_close_helper(item)

# this is a bit of a hack; using implementation details of ParsedXML..
from Products.ParsedXML.PrettyPrinter import _translateCdata, _translateCdataAttr

translateCdata = _translateCdata
translateCdataAttr = _translateCdataAttr

def fix_content_type_header(uploaded_file):
    """Deletes the content-type header on the uploaded_file.
    
    This ensures consistent mimetype assignment for the Silva application
    since Zope will now fallback to the Python database for resolving
    a mimetype.
    """
    if hasattr(uploaded_file, 'headers'):
        if uploaded_file.headers.has_key('content-type'):            
            del uploaded_file.headers['content-type']

# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.6 $
# Silva interfaces
from IVersioning import IVersioning
from IContainer import IContainer
# misc
import urllib

def add_and_edit(self, id, REQUEST):
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
    REQUEST.RESPONSE.redirect(u+'/manage_main')

def unapprove_helper(object):
    """Unapprove object and anything unapprovable contained by it.
    """
    if IVersioning.isImplementedBy(object):
        if object.is_version_approved():
            object.unapprove_version()
    if IContainer.isImplementedBy(object):
        for item in object.get_ordered_publishables():
            unapprove_helper(item)
    
def unapprove_close_helper(object):
    """Unapprove/close object and anything unapprovable/closeable contained by it.
    """
    if IVersioning.isImplementedBy(object):
        if object.is_version_approved():
            object.unapprove_version()
        if object.is_version_published():
            object.close_version()
    if IContainer.isImplementedBy(object):
        for item in object.get_ordered_publishables():
            unapprove_close_helper(item)

# this is a bit of a hack; using implementation details of ParsedXML..
from Products.ParsedXML.PrettyPrinter import _translateCdata, _translateCdataAttr

translateCdata = _translateCdata
translateCdataAttr = _translateCdataAttr


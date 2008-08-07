# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import urllib

# Zope
from zope.interface import implements
from AccessControl import ModuleSecurityInfo

# Silva 
from Products.Silva.interfaces import ISilvaObject, IVersioning, IContainer

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

# this class used to be in SilvaDocument.upgrade, but was moved
# here when Folder._to_folder_or_publication_helper began using it.
class SwitchClass(object):
    """This class can be used to switch an instances class.
       This was used when SilvaDocument was moved to it's own
       product, to switch instances of SilvaDocument and Silva
       Document Version from Products.Silva.Document.Document and
       Products.Silva.Document.DocumentVersion to Products.SilvaDocument.
       Document.Document and DocumentVersion.

       This is also used by Folder._to_folder_or_publication_helper
       to switch a container between folders and publications

       This class conforms to the Silva upgrader API, in that you
       call class.upgrade(obj) to upgrade obj, and the upgraded
       obj is returned"""

    def __init__(self, new_class, args=(), kwargs={}):
        self.new_class = new_class
        self.args = args
        self.kwargs = kwargs

    def upgrade(self, obj):
        obj_id = obj.getId()
        new_obj = self.new_class(obj_id, *self.args, **self.kwargs)
        new_obj.__dict__.update(obj.__dict__)
        container = obj.aq_parent
        setattr(container, obj_id, new_obj)
        new_obj = getattr(container, obj_id)
        return new_obj
   
    def __repr__(self):
        return "<SwitchClass %r>" % self.new_class

#make a container_filter.  See doc/developer_changes for more info
# basically, this returns a closure that can be used for a container filter
# for a content type during product registration.  This closure then
# knows whether the particular content type should be available in
# the zmi add list, whether it should only be visible outside
# of Silva (e.g. the silva root), and the container filter contains
# an extended parameter list to control whether to use the
# lexically-scoped zmi_addable variable when called
def makeContainerFilter(zmi_addable=True, only_outside_silva=False):
    def SilvaZCMLContainerFilter(object_manager, filter_addable=False):
        if filter_addable and not zmi_addable: return False;
        if only_outside_silva:
            if not ISilvaObject.providedBy(object_manager):
                return True
            return False
        else:
            if ISilvaObject.providedBy(object_manager):
                return True
            return False
    return SilvaZCMLContainerFilter

# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import mimetypes
import os
import urllib

# Zope
from Acquisition import aq_parent
from zope.component import getUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent
import zope.deferredimport

# Silva core
from silva.core import interfaces
from silva.core.layout.interfaces import ICustomizableTag

# Load mime.types
mimetypes.init()

_ENCODING_MIMETYPE_TO_ENCODING = {
    'application/x-gzip': 'gzip',
    'application/x-bzip2': 'bzip2',
    }
_CONTENT_ENCODING_EXT = {
    'gzip': '.gz',
    'bzip2': '.bz'
    }
_EXT_CONTENT_ENCODING = {
    '.gz': 'gzip',
    '.bz': 'bzip2'
    }

def create_new_filename(file, basename):
    """Compute and set a new filename for an file. It is composed of
    the given id, basename, where the file extension is changed in
    order to match the format of the file.
    """
    # This function is here to be usable by File and Image
    if not file.get_file_size():
        return

    extension = None
    content_type = file.get_content_type()
    content_encoding = file.get_content_encoding()

    if '.' in basename:
        basename, extension = os.path.splitext(basename)
        if extension in _EXT_CONTENT_ENCODING and '.' in basename:
            if content_encoding is None:
                content_encoding = _EXT_CONTENT_ENCODING[extension]
            basename, extension = os.path.splitext(basename)

    guessed_extension = mimetypes.guess_extension(content_type)
    # Compression extension are not reconized by mimetypes use an
    # extra table for them.
    if guessed_extension is None:
        if (content_type in _ENCODING_MIMETYPE_TO_ENCODING and
            content_encoding is None):
            # Compression extension often are used with some other
            # extension. Unfortunately, at this point we might have
            # lost that other extension. The editor has to rename
            # properly the file.
            content_encoding = _ENCODING_MIMETYPE_TO_ENCODING[content_type]
    elif guessed_extension is not None:
        extension = guessed_extension
    if content_encoding is not None:
        if content_encoding in _CONTENT_ENCODING_EXT:
            if extension is None:
                extension = ''
            extension += _CONTENT_ENCODING_EXT[content_encoding]
    if extension is not None:
        basename += extension
    file.set_filename(basename)


zope.deferredimport.deprecated(
    'Please import directly from silva.core.conf.utils '
    'this import will be removed in Silva 2.4',
    register_service='silva.core.conf.utils:registerService',
    unregister_service='silva.core.conf.utils:unregisterService')


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


def unapprove_close_helper(object):
    """Unapprove/close object and anything unapprovable/closeable
    contained by it.
    """
    if interfaces.IVersioning.providedBy(object):
        if object.is_approved():
            object.unapprove_version()
        if object.is_published():
            object.close_version()
    if interfaces.IContainer.providedBy(object):
        default = object.get_default()
        if default:
            unapprove_close_helper(default)
        for item in object.get_ordered_publishables():
            unapprove_close_helper(item)


# this class used to be in SilvaDocument.upgrade, but was moved
# here when Folder._to_folder_or_publication_helper began using it.
class SwitchClass(object):
    """This class can be used to switch an instances class.

       This is also used by Folder._to_folder_or_publication_helper
       to switch a container between folders and publications

       This class conforms to the Silva upgrader API, in that you
       call class.upgrade(obj) to upgrade obj, and the upgraded
       obj is returned"""

    def __init__(self, cls):
        self.cls = cls

    def upgrade(self, obj):
        # XXX The code here is not valid if you have a reference in
        # the ZODB at an another place than in its folder, because of
        # how the ZODB works. However, in Zope 2, this is never done,
        # because of how the acquisition would not work in that case.
        parent = aq_parent(obj)

        service = getUtility(IIntIds)
        intid = service.queryId(obj)
        if intid is not None:
            reference = service.refs[intid]

        obj.__class__ = self.cls
        obj._p_changed = True
        if '__provides__' in obj.__dict__:
            # Clean up markers UI.
            provided = list(obj.__dict__['__provides__'].interfaces())
            del obj.__dict__['__provides__']
            for iface in provided:
                if iface.extends(ICustomizableTag):
                    alsoProvides(obj, iface)

        if intid is not None:
            # This repickle the reference, with the obj class
            service.refs[intid] = reference
            assert reference.object.__class__ == self.cls

        # Update container
        if parent is not None:
            parent._objects = [
                {'id': oid, 'meta_type': omt}
                if oid != obj.getId()
                else {'id': oid, 'meta_type': obj.meta_type}
                for oid, omt in map(
                    lambda d: (d['id'], d['meta_type']),
                    parent._objects)]
            parent._setOb(obj.getId(), obj)

        notify(ObjectModifiedEvent(obj))
        return obj

    def __repr__(self):
        return "<SwitchClass %r>" % self.cls

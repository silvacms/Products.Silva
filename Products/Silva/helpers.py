# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Python
import urllib

# Zope
from Acquisition import aq_parent
from zope.component import getUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent

# Silva core
from silva.core import interfaces
from silva.core.layout.interfaces import ICustomizableTag


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
            parent._objects = tuple([
                {'id': oid, 'meta_type': omt}
                if oid != obj.getId()
                else {'id': oid, 'meta_type': obj.meta_type}
                for oid, omt in map(
                    lambda d: (d['id'], d['meta_type']),
                    parent._objects)])
            parent._setOb(obj.getId(), obj)

        notify(ObjectModifiedEvent(obj))
        return obj

    def __repr__(self):
        return "<SwitchClass %r>" % self.cls


def convert_content(content, destination_type):
    # This doesn't work.
    switcher = SwitchClass(destination_type)
    target = switcher.upgrade(content)
    return target

# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $
# helper module hiding all the details of cut/copy/paste support

from OFS import CopySupport, Moniker
from OFS.CopySupport import cookie_path, eNotSupported, eNoData, \
     CopyError, _cb_encode, _cb_decode

def create_ref(ob):
    """Create encoded reference to object.
    """
    return _cb_encode(ob.getPhysicalPath())

def resolve_ref(app, ref):
    """Decode and resolve reference to object.
    """
    return app.unrestrictedTraverse(_cb_decode(ref))

def create_oblist(app, refs, check):
    # get all elements to cut
    oblist = []
    for ref in refs:
        # resolve reference to object
        ob = resolve_ref(app, ref)
        # if we can't move the object, give error
        check_method = getattr(ob, check)
        if not check_method():
            raise CopyError, eNotSupported % obj.id
        # construct moniker to object
        m = Moniker.Moniker(ob)
        # add moniker to the list
        oblist.append(m.dump())
    return oblist
    
def cut(app, refs, REQUEST=None):
    """Put refs on the clipboard for cut.
    """
    oblist = create_oblist(app, refs, 'cb_isMoveable')
    # prepare clipboard
    cp = (1, oblist)
    cp = _cb_encode(cp)
    # put encoded clipboard data into cookie if possible
    if REQUEST is not None:
        resp = REQUEST['RESPONSE']
        resp.setCookie('__cp', cp, path='%s' % cookie_path(REQUEST))
        REQUEST['__cp'] == cp
    # always return it
    return cp

def copy(app, refs, REQUEST=None):
    """Put refs on the clipboard for copy.
    """
    oblist = create_oblist(app, refs, 'cb_isCopyable')
    # prepare clipboard
    cp = (0, oblist)
    cp = _cb_encode(cp)
    # put encoded clipboard data into cookie if possible
    if REQUEST is not None:
        resp = REQUEST['RESPONSE']
        resp.setCookie('__cp', cp, path='%s' % cookie_path(REQUEST))
        REQUEST['__cp'] == cp
    # always return it
    return cp
 
def paste(folder, cb_copy_data=None, REQUEST=None):
    """Paste previously copied objects into Folder.
    """
    if cb_copy_data:
        folder.manage_pasteObjects(cb_copy_data)
    elif REQUEST and REQUEST.has_key('__cp'):
        folder.manage_pasteObjects(REQUEST['__cp'])
    else:
        raise CopyError, eNoData

def delete(app, refs):
    """Delete refs.
    """
    for ref in refs:
        ob = resolve_ref(app, ref)
        ob.aq_parent.manage_delObjects([ob.id])


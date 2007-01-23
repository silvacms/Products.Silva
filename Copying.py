# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.7 $
# helper module hiding all the details of cut/copy/paste support

from OFS.CopySupport import _cb_encode, _cb_decode

def create_ref(ob):
    """Create encoded reference to object.
    """
    return _cb_encode(ob.getPhysicalPath())

def resolve_ref(app, ref):
    """Decode and resolve reference to object.
    """
    return app.unrestrictedTraverse(_cb_decode(ref))

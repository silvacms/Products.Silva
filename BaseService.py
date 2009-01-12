# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements
from OFS import SimpleItem

import interfaces
from silva.core import conf as silvaconf

class ZMIObject(SimpleItem.SimpleItem):

    silvaconf.baseclass()

    implements(interfaces.IZMIObject)

class SilvaService(ZMIObject):

    implements(interfaces.ISilvaService)

    silvaconf.baseclass()

    def __init__(self, id, title):
        self.id = id
        self.title = title


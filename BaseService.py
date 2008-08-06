# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements
from OFS import SimpleItem

import interfaces
from silva.core import conf

class ZMIObject(SimpleItem.SimpleItem):

    conf.baseclass()

class SilvaService(ZMIObject):

    implements(interfaces.ISilvaService)

    conf.baseclass()

    def __init__(self, id, title):
        self.id = id
        self.title = title


# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.5 $
import Interfaces
from SilvaObject import SilvaObject
from Globals import InitializeClass
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo

class Asset(SilvaObject, SimpleItem.SimpleItem):
    __implements__ = Interfaces.Asset
    
    pass

    

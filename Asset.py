# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.6 $
# Zope
from Globals import InitializeClass
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
# Silva interfaces
from IAsset import IAsset
# Silva
from SilvaObject import SilvaObject

class Asset(SilvaObject, SimpleItem.SimpleItem):
    __implements__ = IAsset
    
    pass

    

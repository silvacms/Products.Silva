# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.7 $
# Zope
from Globals import InitializeClass
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
# Silva interfaces
from IAsset import IAsset
# Silva
from SilvaObject import SilvaObject
import SilvaPermissions

class Asset(SilvaObject, SimpleItem.SimpleItem):
    __implements__ = IAsset

    security = ClassSecurityInfo()
        
InitializeClass(Asset)

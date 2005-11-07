from __future__ import nested_scopes

import string
import re
import os

# zope imports
import zLOG
from Globals import package_home
from AccessControl import Owned

# silva imports
from Products.Silva.interfaces import IUpgrader, IContainer, IContent, \
        IVersion, IVersionedContent
from Products.Silva import upgrade
from Products.Silva.adapters import security
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.VersionedContent import VersionedContent
from Products.SilvaMetadata.Exceptions import BindingError

import zLOG
import sys

#-----------------------------------------------------------------------------
# 0.9.3 to 1.0.0
#-----------------------------------------------------------------------------

class ImageUpgrade:
    """handle view registry beeing moved out of the core"""

    __implements__ = IUpgrader

    def upgrade(self, image):
        if image.hires_image is None:
            image.hires_image = image.image
        try:
            image._createDerivedImages()
        except:
            exc, e, tb = sys.exc_info()
            del tb
            zLOG.LOG('Silva', zLOG.WARNING,
                    ('Error upgrading image %s: %s - %s; the image object is '
                    'probably broken.') % (image.absolute_url(), exc, e))
        return image
            
class RefreshAll:
    " refresh all products "

    __implements__ = IUpgrader

    def upgrade(self, root):
        zLOG.LOG('Silva', zLOG.INFO, 'refresh all installed products') 
        root.service_extensions.refresh_all()
        return root
    
def initialize():
    upgrade.registry.registerUpgrader(ImageUpgrade(), '1.0', 'Silva Image')
    upgrade.registry.registerUpgrader(RefreshAll(), '1.0', 'Silva Root')

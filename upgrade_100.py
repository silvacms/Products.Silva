from zope.interface import implements

# silva imports
from Products.Silva.interfaces import IUpgrader
from Products.Silva import upgrade

import zLOG
import sys

#-----------------------------------------------------------------------------
# 0.9.3 to 1.0.0
#-----------------------------------------------------------------------------

class ImageUpgrade:
    """handle view registry beeing moved out of the core"""

    implements(IUpgrader)

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

    implements(IUpgrader)

    def upgrade(self, root):
        zLOG.LOG('Silva', zLOG.INFO, 'refresh all installed products') 
        root.service_extensions.refresh_all()
        return root
    
def initialize():
    upgrade.registry.registerUpgrader(ImageUpgrade(), '1.0', 'Silva Image')
    upgrade.registry.registerUpgrader(RefreshAll(), '1.0', 'Silva Root')

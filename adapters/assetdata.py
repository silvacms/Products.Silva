# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: assetdata.py,v 1.5 2005/11/14 18:06:13 faassen Exp $
#

# XXX These asset adapters are a temporary solution and will not be
# necessary once the assets get a consistent API

from zope.interface import implements

import Globals
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces

class FileData(adapter.Adapter):
    
    implements(interfaces.IAssetData)

    def _getDataForFile(self, file):
        if file.meta_type == 'File': # OFS.Image.File
            return str(file.data)
        elif file.meta_type == 'ExtFile': # ExtFile.ExtFile.ExtFile
            ref = file._get_fsname(file.get_filename())
            return open(ref, 'rb').read()
        else:
            return None
    
    def getData(self):
        file = self.context._file
        return self._getDataForFile(file)
    
class FlashData(FileData):
    
    implements(interfaces.IAssetData)

    def getData(self):
        file = self.context._flash
        return self._getDataForFile(file)

class ImageData(adapter.Adapter):
    
    implements(interfaces.IAssetData)

    def getData(self):
        image = getattr(self.context, 'hires_image', None)
        if image is None:
            # Fallback to 'normal' image, which, if there isn't a hires
            # version, should be the original.
            image = self.context.image
        if image.meta_type == 'Image': # OFS.Image.Image
            return str(image.data)
        elif image.meta_type == 'ExtImage': # ExtFile.ExtImage.ExtImage
            ref = image._get_fsname(image.get_filename())
            return open(ref, 'rb').read()
        else:
            return None
    
def getAssetDataAdapter(context):
    if context.meta_type == 'Silva File':
        return FileData(context)
    elif context.meta_type == 'Silva Image':
        return ImageData(context)
    elif context.meta_type == 'Silva Flash':
        return FlashData(context)
    return None
            

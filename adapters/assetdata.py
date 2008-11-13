# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# XXX These asset adapters are a temporary solution and will not be
# necessary once the assets get a consistent API

from five import grok
from Products.Silva import interfaces

class FileData(grok.Adapter):

    grok.implements(interfaces.IAssetData)
    grok.context(interfaces.IFile)

    def getData(self):
        return self.context.get_content()

class ImageData(grok.Adapter):

    grok.implements(interfaces.IAssetData)
    grok.context(interfaces.IImage)

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


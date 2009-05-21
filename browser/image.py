from Products.Five import BrowserView
class resize_image_from_kupu(BrowserView):
    """This view is called from kupu when an image resize is confirmed.
       The zcml has restricted this to silva authors only.  The REQUEST
       has a width and height, and if they are valid, the web format
       image is resized"""
    def __call__(self):
        try:
            width = int(self.request.width)
            height = int(self.request.height)
        except:
            raise AttributeError,"width or height are not numbers"
        if width < 1:
            width = 1
        if height < 1:
            height = 1
        self.context.set_web_presentation_properties(self.context.getWebFormat(),
                                                     "%sx%s"%(width,height),
                                                     self.context.getWebCrop())

        return "done"
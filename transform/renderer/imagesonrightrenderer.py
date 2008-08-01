
# Silva
from Products.Silva.transform.renderer.xsltrendererbase import XSLTRendererBase

class ImagesOnRightRenderer(XSLTRendererBase):
    def __init__(self):
        XSLTRendererBase.__init__(self, 'images_to_the_right.xslt', __file__)

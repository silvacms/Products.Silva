# Silva
from Products.Silva.transform.renderer.xsltrendererbase import XSLTRendererBase

class NoTitleRenderer(XSLTRendererBase):
    def __init__(self):
        XSLTRendererBase.__init__(self, 'no_title.xslt', __file__)

# Silva
from Products.Silva.transform.renderer.xsltrendererbase import XSLTRendererBase

class BasicXSLTRenderer(XSLTRendererBase):
    def __init__(self):
        XSLTRendererBase.__init__(self, 'normal_view.xslt', __file__)

#!/usr/bin/python
import os

# Silva
from Products.Silva.transform.renderer.xsltrendererbase import XSLTRendererBase

class BasicXSLTRenderer(XSLTRendererBase):
    def __init__(self):
        XSLTRendererBase.__init__(self)
        self._stylesheet_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "normal_view.xslt")
        self._stylesheet = None

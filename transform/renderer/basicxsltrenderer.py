#!/usr/bin/python
import os

# Zope
from Globals import InitializeClass

# Silva
from Products.Silva.transform.renderer.xsltrendererbase import XSLTRendererBase

class BasicXSLTRenderer(XSLTRendererBase):
    def __init__(self):
        XSLTRendererBase.__init__(self)

        self._name = 'Basic HTML (New Version)'
        self._stylesheet_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "normal_view.xslt")
        self._stylesheet = None

InitializeClass(BasicXSLTRenderer)

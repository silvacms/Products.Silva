#!/usr/bin/python
import os

# Zope
from Globals import InitializeClass

# Silva
from Products.Silva.transform.renderers.XSLTRendererBase import XSLTRendererBase

class BasicRenderer(XSLTRendererBase):
    def __init__(self):
        self._name = 'Basic HTML (New Version)'
        self._stylesheet = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "normal_view.xslt")

InitializeClass(BasicRenderer)

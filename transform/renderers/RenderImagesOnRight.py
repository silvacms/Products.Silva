#!/usr/bin/python
import os

# Zope
from Globals import InitializeClass

# Silva
from Products.Silva.transform.renderers.XSLTRendererBase import XSLTRendererBase

class RenderImagesOnRight(XSLTRendererBase):
    def __init__(self):
        XSLTRendererBase.__init__(self)

        self._name = 'Images on Right'
        self._stylesheet_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "images_to_the_right.xslt")
        self._stylesheet = None

InitializeClass(RenderImagesOnRight)

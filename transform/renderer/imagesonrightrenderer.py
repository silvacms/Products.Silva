#!/usr/bin/python
import os

# Zope
from Globals import InitializeClass

# Silva
from Products.Silva.transform.renderer.xsltrendererbase import XSLTRendererBase

class ImagesOnRightRenderer(XSLTRendererBase):
    def __init__(self):
        XSLTRendererBase.__init__(self)

        # for creating your own renderer, copying this file, and 
        # modifying the self._name and the filename of the stylesheet
        # should be enough

        self._name = 'Images on Right'
        self._stylesheet_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "images_to_the_right.xslt")
        self._stylesheet = None

InitializeClass(ImagesOnRightRenderer)

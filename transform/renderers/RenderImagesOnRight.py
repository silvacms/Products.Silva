#!/usr/bin/python

from Products.Silva.transform.interfaces import IRenderer

class RenderImagesOnRight(object):

    __implements__ = IRenderer

    def render(self, obj):
        # FIXME: this is obviously just a stub implementation, as the
        # hard(ish) part is getting the architecture working together,
        # not the implementation details of applying the stylesheet
        # to the XML. FIX THIS METHOD once the architecture works itself
        # out a bit.
        return "images on right"

    def getName(self):
        return "Images on Right"

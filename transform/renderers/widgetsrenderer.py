#!/usr/bin/python

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
import Acquisition

# Silva
from Products.Silva.transform.interfaces import IRenderer

class WidgetsRenderer(Acquisition.Implicit):

    __implements__ = IRenderer

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    security.declareProtected("View", "render")
    def render(self, version):
        node = version.content.documentElement
        self.service_editor.setViewer("service_doc_viewer")
        return self.service_editor.renderView(node)

    security.declareProtected("View", "getName")
    def getName(self):
        return "Basic HTML"

InitializeClass(WidgetsRenderer)

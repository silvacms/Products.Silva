from Products.Silva.transform.interfaces import IRenderer

class HelloWorldRenderer(object):

    __implements__ = IRenderer

    def __init__(self):
        self._id = "HelloWorldRenderer"
        self._name = "Hello World"

    def render(self, obj):
        pass

    def setName(self, name):
        self._name = name

    def getName(self):
        return self._name

    def getId(self):
        return self._id

    def setId(self, renderer_id):
        self._id = renderer_id

    def supportsMetaType(self, meta_type):
        pass

    def getSupportedMetaTypes(self):
        pass

    def setSupportedMetaTypes(self):
        pass

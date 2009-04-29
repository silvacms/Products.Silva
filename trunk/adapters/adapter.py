import Acquisition

class Adapter(Acquisition.Explicit):
    def __init__(self, context):
        self.context = context
        
    def getContext(self):
        return self.context.aq_inner

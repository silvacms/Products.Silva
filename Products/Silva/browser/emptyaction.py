from Products.Five import BrowserView

class EmptyAction(BrowserView):
    
    def __call__(self):
        # by default, there's no additional action
        return ''

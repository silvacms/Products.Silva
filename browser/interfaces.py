from zope.interface import Interface

class ISubscriptorView(Interface):
    def render(self):
        """pass"""

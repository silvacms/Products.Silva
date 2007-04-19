from zope import interface
from zope import component
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserRequest

from ZPublisher.BaseRequest import DefaultPublishTraverse

from Products.Silva.browser.skin.interfaces import ISilvaSkin
from Products.Silva.interfaces import IRoot

class SkinSwitcher(DefaultPublishTraverse):
    component.adapts(IRoot, IBrowserRequest)

    def __init__(self, context, request):
        super(SkinSwitcher, self).__init__(context, request)
        # TODO: Use an adapter for figuring out what skin we really
        # want to set
        interface.alsoProvides(request, ISilvaSkin)

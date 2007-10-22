from zope.interface import implements
from zope.app.pagetemplate import ViewPageTemplateFile

from zExceptions import NotFound
from Products.Five import BrowserView

from Products.Silva import subscriptionerrors as errors
from Products.Silva.i18n import translate as _
from Products.Silva.adapters import subscribable
from Products.Silva.interfaces import ISilvaObject

from interfaces import ISubscriptorView

from zLOG import LOG,INFO

class Subscriptor(BrowserView):

    __render__ = ViewPageTemplateFile("subscriptor_view.pt")
    
    def try_subscribe(self):
        emailaddress = self.request.get("emailaddress","")
        #a subscription or unsubscription attempt
        try:
            self.service.requestSubscription(self.context,
                                             emailaddress)
        except errors.NotSubscribableError, e:
            return self.context.subscriptor(
                message_type='warning',
                message=_('content is not subscribable'), 
                subscr_emailaddress=emailaddress)
        except errors.InvalidEmailaddressError, e:
            return context.subscriptor(
                message_type='warning',
                message=_('emailaddress not valid'), 
                subscr_emailaddress=emailaddress)
        except (errors.AlreadySubscribedError, errors.NotSubscribedError), e:
            # We just pretend to have sent email in order not to expose
            # any information on the validity of the email address
            pass
        mailedmessage = _(
            'Confirmation request for subscription has been emailed to ${emailaddress}')
        mailedmessage.set_mapping({'emailaddress': emailaddress})
        return self.__render__(message=mailedmessage,
                               message_type='feedback',
                               show_form=False)

    def try_unsubscribe(self):
        emailaddress = self.request.get("emailaddress","")
        try:
            self.service.requestCancellation(self.context, emailaddress)
        except errors.NotSubscribableError, e:
            return context.subscriptor(
                message=_('content is not subscribable'), 
                message_type='warning',
                subscr_emailaddress=emailaddress)
        except errors.InvalidEmailaddressError, e:
            return context.subscriptor(
                message=_('emailaddress not valid'), 
                message_type='warning',
                subscr_emailaddress=emailaddress)
        except (errors.AlreadySubscribedError, errors.NotSubscribedError), e:
            # We just pretend to have sent email in order not to expose
            # any information on the validity of the emailaddress
            pass
        
        mailedmessage = _(
            'Confirmation request for cancellation has been emailed to ${emailaddress}')
        mailedmessage.set_mapping({'emailaddress': emailaddress})

        return self.__render__(message=mailedmessage,
                               message_type='feedback',
                               show_form=False)

    def do_subscriptor(self):
        #get the subscribable adapter for this context
        self.adapted = subscribable.getSubscribable(self.context)

        # see if content is subscribable
        if self.adapted is None:
            raise NotFound
        elif not self.adapted.isSubscribable(): 
            raise errors.NotSubscribableError()

        self.service = self.context.service_subscriptions
        self.request = self.context.REQUEST
        self.request.RESPONSE.setHeader('Content-Type', 'text/html; charset=UTF-8');

        #thiscontent = ISubscriptorView(self.context)
        LOG('tc',INFO,self.request.getPresentationSkin())
        #return thiscontent()

        if self.request.has_key("subscribe"):
            return self.context.try_subscribe()
        elif self.request.has_key("unsubscribe"):
            return self.context.try_unsubscribe()
        skin = self.context.restrictedTraverse(["++skin++"+self.request.getPresentationSkin()])

        from zope.component import getUtility, getGlobalServices, getGlobalService, getServices, getService

        gps = getService("Presentation",self.context)
        newcontext = ISubscriptorView(self.context)
        LOG('newc',INFO,newcontext)
        #LOG('skin',INFO,self.request._skins[skin])
        return self.__render__()

from Products.Silva.adapters import adapter
class SubscriptorView(object):
    implements(ISubscriptorView)

    def __init__(self, context):
        self.context = context

    def render(self, a, b):
        return "rendering"

    def __getitem__(self, item):
        return self.context.__getitem__(item)
        





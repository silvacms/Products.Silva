from Products.Silva import subscriptionerrors
from Products.Silva.i18n import translate as _

request = context.REQUEST
service = context.service_subscriptions

try:
    service.unsubscribe(
        request['ref'], request['emailaddress'], request['token'])
except subscriptionerrors.CancellationError, e:
    return context.subscriptor(
        message=_(
            'Something went wrong in unsubscribing from this page. '
            'It might be that the link you followed expired.'), 
        show_form=False)
        
return context.subscriptor(
    message=_('You have been successfully unsubscribed.'), show_form=False)

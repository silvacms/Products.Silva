from Products.Silva import subscriptionerrors
from Products.Silva.i18n import translate as _

request = context.REQUEST
service = context.service_subscriptions

try:
    service.requestCancellation(request['path'], request['emailaddress'])
except subscriptionerrors.EmailaddressError, e:
    # We just pretend to have sent email in order not to expose
    # any information on the validity of the emailaddress
    pass
except subscriptionerrors.SubscriptionError, e:
    return str(e)

return context.subscriptions(message=_('Confirmation request for cancellation has been emailed'))

from Products.Silva import subscriptionerrors as errors
from Products.Silva.i18n import translate as _

request = context.REQUEST
service = context.service_subscriptions

content = context.restrictedTraverse(request['path'], None)
if content is None:
    return context.subscriptions(
        message=_('Path does not lead to a content object'))

try:
    service.requestSubscription(content, request['emailaddress'])
except (errors.AlreadySubscribedError, errors.NotSubscribedError), e:
    # We just pretend to have sent email in order not to expose
    # any information on the validity of the emailaddress
    pass
except errors.SubscriptionError, e:
    return context.subscriptions(
        message=_(e), subscr_emailaddress=request['emailaddress'])

return context.subscriptions(
    message=_('Confirmation request for subscription has been emailed'))

from Products.Silva import subscriptionerrors
from Products.Silva.i18n import translate as _

request = context.REQUEST
service = context.service_subscriptions

try:
    service.subscribe(
        request['ref'], request['emailaddress'], request['token'])
except subscriptionerrors.SubscriptionError, e:
    return context.subscriptions(
        message=_('Subscription failed'), show_form=False)

return context.subscriptions(
    message=_('Subscription successful'), show_form=False)

from Products.Silva import subscriptionerrors
from Products.Silva.i18n import translate as _

request = context.REQUEST
service = context.service_subscriptions

try:
    service.subscribe(
        request['ref'], request['emailaddress'], request['token'])
except subscriptionerrors.SubscriptionError, e:
    return context.subscriptor(
        message=_('Subscription failed'), show_form=False)

return context.subscriptor(
    message=_(
        'You have been successfully subscribed. '
        'This means you will receive email notifications '
        'whenever a new version of these pages becomes available.'), 
        show_form=False)

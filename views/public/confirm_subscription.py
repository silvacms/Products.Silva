from Products.Silva import subscriptionerrors

request = context.REQUEST
service = context.service_subscriptions

try:
    service.subscribe(
        request['ref'], request['emailaddress'], request['token'])
except subscriptionerrors.SubscriptionError, e:
    return 'Subscription failed'

return 'Subscription succesful'

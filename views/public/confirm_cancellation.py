from Products.Silva import subscriptionerrors

request = context.REQUEST
service = context.service_subscriptions

try:
    service.unsubscribe(
        request['ref'], request['emailaddress'], request['token'])
except subscriptionerrors.SubscriptionError, e:
    return 'Cancellation failed'

return 'Cancellation succesful'
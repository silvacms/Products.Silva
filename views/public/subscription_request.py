from Products.Silva import subscriptionerrors

request = context.REQUEST
service = context.service_subscriptions

try:
    service.requestSubscription(request['path'], request['emailaddress'])
except subscriptionerrors.EmailaddressError, e:
    # We just pretend to have sent email in order not to expose
    # any information on the validity of the emailaddress
    pass
except subscriptionerrors.SubscriptionError, e:
    return str(e)

return 'Confirmation request for subscription has been emailed'
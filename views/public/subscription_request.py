from Products.Silva import subscriptionerrors as errors

request = context.REQUEST
service = context.service_subscriptions

content = context.restrictedTraverse(request['path'], None)
if content is None:
    return context.subscriptions_ui(
        message='Path does not lead to a content object')

try:
    service.requestSubscription(content, request['emailaddress'])
except (errors.AlreadySubscribedError, errors.NotSubscribedError), e:
    # We just pretend to have sent email in order not to expose
    # any information on the validity of the emailaddress
    pass
except errors.SubscriptionError, e:
    return context.subscriptions_ui(
        message=e, subscr_emailaddress=request['emailaddress'])

return context.subscriptions_ui(
    message='Confirmation request for subscription has been emailed',
    show_form=False)

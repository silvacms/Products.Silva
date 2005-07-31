from Products.Silva import subscriptionerrors as errors
from Products.Silva.i18n import translate as _

request = context.REQUEST
service = context.service_subscriptions

content = context.restrictedTraverse(request['path'], None)
if content is None:
    return context.subscriptor(
        message_type='warning',
        message=_('Path does not lead to a content object'))

try:
    service.requestSubscription(content, request['emailaddress'])
except errors.NotSubscribableError, e:
    return context.subscriptor(
        message_type='warning',
        message=_('content is not subscribable'), 
        subscr_emailaddress=request['emailaddress'])
except errors.InvalidEmailaddressError, e:
    return context.subscriptor(
        message_type='warning',
        message=_('emailaddress not valid'), 
        subscr_emailaddress=request['emailaddress'])
except (errors.AlreadySubscribedError, errors.NotSubscribedError), e:
    # We just pretend to have sent email in order not to expose
    # any information on the validity of the email address
    pass

mailedmessage = _(
    'Confirmation request for subscription has been emailed to ${emailaddress}')
mailedmessage.set_mapping({'emailaddress': request['emailaddress']})

return context.subscriptor(message=mailedmessage, message_type='feedback', show_form=False)
    

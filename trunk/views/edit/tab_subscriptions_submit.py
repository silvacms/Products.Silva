from Products.Formulator.Errors import ValidationError, FormValidationError
from Products.Silva.adapters import subscribable

request = context.REQUEST
model = request.model
service = context.service_subscriptions
if not service.subscriptionsEnabled():
    return

adapter = subscribable.getSubscribable(model)
if adapter is None:
    return

try:
    result = context.tab_subscriptions_form.validate_all(request)
except FormValidationError, e:
    return context.tab_subscriptions(
        message_type='error', message=context.render_form_errors(e))

s = result['subscribable']
adapter.setSubscribability(int(s))

# emtpy the subscriptions first
for emailaddress in adapter.getSubscribedEmailaddresses():
    adapter.unsubscribe(emailaddress)
# then fill it with current setting
for emailaddress in result['subscriptions']:
    adapter.subscribe(emailaddress)

return context.tab_subscriptions(
    message='Subscription settings saved', message_type='feedback')

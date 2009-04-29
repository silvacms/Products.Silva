from Products.Silva.adapters import subscribable

request = context.REQUEST
model = request.model

adapter = subscribable.getSubscribable(model)
if adapter is None:
    subscriptions = []
else:
    subscriptions = list(adapter.getSubscribedEmailaddresses())
    subscriptions.sort()

# Set request variables, used by tab_subscriptions.pt
# and tab_subscriptions_form.form
request.set('subscribable', adapter)
request.set('subscriptions', subscriptions)

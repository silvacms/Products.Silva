from Products.Silva.adapters import subscribable

request = context.REQUEST
model = request.model
adapter = subscribable.getSubscribable(model)
if adapter is None:
    return False

return context.service_subscriptions.subscriptionsEnabled()
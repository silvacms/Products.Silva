from Products.Silva.adapters.security import getLockAdapter

return getLockAdapter(context.REQUEST.model).isLocked()

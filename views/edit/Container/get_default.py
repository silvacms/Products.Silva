##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
# return default document if available and visible
model = context.REQUEST.model
default = model.get_default()
if default is None:
    return default
view_registry = context.service_view_registry
view = view_registry.get_view('public', default.meta_type)
# if there is *NO* visibility info, the document *IS* visible
visible = getattr(view, 'visible', lambda: 1)
if visible():
    return default
return None



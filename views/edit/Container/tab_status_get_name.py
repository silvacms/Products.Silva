## Script (Python) "tab_status_get_name"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model
##title=
##
if not model.is_default():
    return model.id
else:
    return '%s of %s' % (model.id, model.get_container().getId())

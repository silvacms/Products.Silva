## Script (Python) "has_focus_box"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=tab_id
##title=
##
if not tab_id == 'tab_edit':
    return 0
model = context.REQUEST.model
version = model.get_unapproved_version()
if version is None:
    return 0
document = getattr(model, version)
widget_path = context.service_editor.getNodeWidgetPath(context.service_editor.getRoot(document.documentElement))
if widget_path is None:
    return
return widget_path[-1] == 'mode_edit'

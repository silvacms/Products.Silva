## Script (Python) "get_edit_mode"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
session_data = context.REQUEST.SESSION.get('silva_field_edit_mode')
if session_data is None:
    return "normal"
return session_data.get(context.REQUEST.model.getPhysicalPath(), 'normal')

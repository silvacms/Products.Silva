## Script (Python) "set_edit_mode"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=mode
##title=
##
session = context.REQUEST.SESSION
session_data = session.get('silva_field_edit_mode', {})
session_data[context.REQUEST.model.getPhysicalPath()] = mode
session['silva_field_edit_mode'] = session_data

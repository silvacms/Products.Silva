## Script (Python) "edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
view = context
model = context.REQUEST.model

edit_mode = context.get_edit_mode()

if edit_mode is None:
    edit_mode = 'normal'

if edit_mode == 'normal':
    return view.normal_edit()
elif edit_mode == 'content':
    return view.content_edit()

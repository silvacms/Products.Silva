## Script (Python) "submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
view = context
model.haunt()
return view.tab_edit(message_type="feedback",
    message="Ghost Folder synchronised")

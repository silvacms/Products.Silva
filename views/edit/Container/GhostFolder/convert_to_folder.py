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

id = model.id
parent = model.aq_parent
model.to_folder()
model = getattr(parent, id)
context.REQUEST.set('model', model)
return model.edit['tab_edit'](message_type="feedback",
    message="Ghost Folder has been replaced by a folder")


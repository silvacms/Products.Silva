## Script (Python) "tab_edit_to_publication"
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

if model.meta_type != 'Silva Folder':
    return view.tab_edit(message_tye="error",
                         message="Can only change Folders into Publications")

id = model.id
parent = model.aq_parent
model.to_publication()
model = getattr(parent, id)
context.REQUEST.set('model', model)
message = "Changed into publication"
return model.edit['tab_metadata'](message_type="feedback", message=message)

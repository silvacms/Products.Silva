model = context.REQUEST.model
view = context

if model.meta_type != 'Silva Publication':
    return view.tab_edit(message_tye="error",
                         message="Can only change Publications into Folders")

id = model.id
parent = model.aq_parent
model.to_folder()
model = getattr(parent, id)
context.REQUEST.set('model', model)
message = "Changed into publication"
return model.edit['tab_edit'](message_type="feedback", message=message)

##parameters=model, id, title, result
model.manage_addProduct['Silva'].manage_addDocument(id, title)
document = getattr(model, id)

#subject = result['subject'] or ''
#document.manage_addProperty('subject', subject, 'string')

return document

## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result
##title=
##
model.manage_addProduct['Silva'].manage_addDocument(id, title)
document = getattr(model, id)

subject = result['subject'] or ''
document.manage_addProperty('subject', subject, 'string')        

return document

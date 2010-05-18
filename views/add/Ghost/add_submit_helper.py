## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result
##title=
##
content_url = result['content_url']

model.manage_addProduct['Silva'].manage_addGhost(
    id, None, haunted_url=content_url)
return getattr(model, id)

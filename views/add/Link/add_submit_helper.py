## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result
##title=
##
url = result['url']
model.manage_addProduct['Silva'].manage_addLink(
    id, 
    title, 
    url)
return getattr(model, id)

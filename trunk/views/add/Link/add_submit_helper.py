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
link_type = result['link_type']
model.manage_addProduct['Silva'].manage_addLink(
    id, 
    title, 
    url, 
    link_type=link_type)
return getattr(model, id)

## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result
##title=
##
depth = result['depth']
model.manage_addProduct['Silva'].manage_addAutoTOC(id, title, depth)
toc = getattr(model, id)
return toc

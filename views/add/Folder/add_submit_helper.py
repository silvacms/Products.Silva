## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result
##title=
##
policy_name = result['policy_name']
model.manage_addProduct['Silva'].manage_addFolder(
    id, title, policy_name=policy_name)
    
return getattr(model, id)

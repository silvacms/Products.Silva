## Script (Python) "tab_preview_needs_feedback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model

if model.implements_container() and model.get_default():
    model = model.get_default()

return (model.implements_versioning() 
    and not model.get_next_version() 
    and not model.get_public_version())

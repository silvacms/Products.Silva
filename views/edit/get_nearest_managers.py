## Script (Python) "get_nearest_managers"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
return [model.sec_get_user_info(userid) for userid in          
        model.sec_get_nearest_of_role('Manager')]

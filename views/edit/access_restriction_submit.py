## Script (Python) "access_restriction_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model

msg = ""
value = context.REQUEST.form.get('access_restriction', '')
id = 'access_restriction'

if value:
    if model.hasProperty(id):
        if not model.getProperty(id) == value:            
            model.manage_changeProperties({id:value})
            msg = "Restriction changed"
    else:
        model.manage_addProperty(id, value, 'string')
        msg = "Restriction set"
else:
    if model.hasProperty(id):
        model.manage_delProperties([id])
    msg = "Restriction cleared"

return context.tab_access(message_type="feedback", message=msg)

## Script (Python) "minimal_access_role_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
view = context
request = view.REQUEST
model = request.model

message = ''

new_minimal_role = request['role']

# XXX This stuff is now tailormade for the situation, should work with more than 2 options in the future
if new_minimal_role != 'None':
    if not model.sec_is_closed_to_public():
        model.sec_close_to_public()
        message = 'Object is now closed to unauthenticated users'
    else:
        message = 'Object was already closed to unauthenticated users'
else:
    if model.sec_is_closed_to_public():
        model.sec_open_to_public()
        message = 'Object is now open to unauthenticated users'
    else:
        message = 'Object was already open to unauthenticated users'

return model.edit['tab_access'](message_type='feedback', message=message)

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
old_minimal_role = model.sec_minimal_view_role()

# XXX This stuff is now tailormade for the situation, should work with more than 2 options in the future
if new_minimal_role == 'Anonymous' and old_minimal_role != 'Anonymous':
    model.sec_open_to_public()
    message = 'No restriction is applied (open to the public)'
elif new_minimal_role == 'Authenticated' and old_minimal_role != 'Authenticated':
    model.sec_close_to_public(1)
    message = 'Minimal role for viewing is now set to Authenticated'
elif new_minimal_role == 'Viewer' and old_minimal_role != 'Viewer':
    model.sec_close_to_public(0)
    message = 'Minimal role for viewing is now set to Viewer'
elif new_minimal_role == old_minimal_role:
    message = 'Minimal role has not changed'

return model.edit['tab_access'](message_type='feedback', message=message)

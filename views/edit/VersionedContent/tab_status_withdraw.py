## Script (Python) "tab_status_withdraw"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Withdraw a request for approval on unapproved content
##
request = context.REQUEST
model = request.model

# XXX fishy: if no message, we are called from the edit tab ...
if request.has_key('message'):
  message = request['message']
  view  = context.tab_status
else:
  message = '''
Withdraw request for approval via the edit tab. 
(Automatically generated message)
'''
  view = context.tab_edit
 
if model.get_unapproved_version() is None:
  if model.get_public_version() is not None:
    if view.get_silva_permissions()['ApproveSilvaContent']:
      return view(message_type="error", message="This content object is already public. You can close the current public version.")
    else:
      return view(message_type="error", message="This content object is already public.")
  else:
    return view(message_type="error", message="This content object is already approved. You can revoke the approval.")

if not model.is_version_approval_requested():
    return view(message_type="error", message="No request for approval is pending for this content object.")

model.set_approval_request_message(message)
model.withdraw_version_approval()

return view(message_type="feedback", message="Withdrawn request for approval.")

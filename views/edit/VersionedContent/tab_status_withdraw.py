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

is_rejection = request['rejection_status'] == 'true'

# XXX fishy: if no message, we are called from the edit tab ...
# also use dummy message, if author leaves input box empty
message = request.get('message','')
if message:
  view  = context.tab_status
else:
  tab_name = request['tab_name']
  if is_rejection:
    message = '''\
Rejected request for approval via the %s tab.
(Automatically generated message)
''' % tab_name
  else:
    message = '''\
Withdrew request for approval via the %s tab. 
(Automatically generated message)
''' % tab_name
  # next fish
  if tab_name == 'edit':
    view = context.tab_edit
  else:
    view = context.tab_status


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


if is_rejection:
  model.reject_version_approval(message)
else:
  model.withdraw_version_approval(message)

if hasattr(model, 'service_messages'):
  model.service_messages.send_pending_messages()

if is_rejection:
  message = 'Rejected request for approval'
else:
  message = 'Withdrew request for approval'

return view(message_type="feedback", message=message)

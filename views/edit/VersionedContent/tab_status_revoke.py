## Script (Python) "tab_status_revoke"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Revoke approval of approved content
##
model = context.REQUEST.model
view = context

if not model.is_approved():
  return view.tab_status(message_type="error", message="This content is not approved.")
  

model.unapprove_version()

return view.tab_status(message_type="feedback", message="Revoked approval.")

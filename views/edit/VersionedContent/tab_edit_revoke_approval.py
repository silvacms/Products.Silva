## Script (Python) "tab_edit_revoke_approval"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
view = context
model.unapprove_version()
return view.tab_edit(message_type="feedback", message="Revoked approval")

## Script (Python) "properties_revoke_approval"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
model.unapprove_version()
return context.tab_metadata(message_type="feedback", message=_("Revoked approval."))

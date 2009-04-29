## Script (Python) "tab_access_deny_access"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.i18n import translate as _
from zope.i18n import translate

request = context.REQUEST
model = request.model

if not request.has_key('requests') or not request['requests']:
    return context.tab_access(message_type='error', message=_('No requests selected'))

messages = []
for userid, role in [r.split('|') for r in request['requests']]:
    model.deny_role(userid, role)
    msg = _('&#xab;${user_id}&#xbb; has been denied the ${role} role',
            mapping={'user_id': userid, 'role': role})
    messages.append(translate(msg))

model.send_messages()

return context.tab_access(message_type='feedback', message=', '.join(messages))

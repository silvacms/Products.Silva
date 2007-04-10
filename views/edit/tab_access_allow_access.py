## Script (Python) "tab_access_allow_access"
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

view = context
request = view.REQUEST
model = request.model

if not request.has_key('requests') or not request['requests']:
    return view.tab_access(message_type='error', message=_('No requests selected'))

messages = []
for userid, role in [r.split('|') for r in request['requests']]:
    try:
        model.allow_role(userid, role)
    except Exception, e:
        return view.tab_access(message_type='error', message=e) 
    msg = _('&#xab;${user_id}&#xbb; allowed the ${role} role',
            mapping={'user_id': userid, 'role': role})
    messages.append(translate(msg))

model.send_messages()

return view.tab_access(message_type='feedback', message=', '.join(messages))

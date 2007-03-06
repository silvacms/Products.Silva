from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model
view = context

model.set_allow_feeds(False)
if request.form.has_key('allow_feeds'):
    model.set_allow_feeds(True)

type = 'feedback'
msg = _('Feed settings saved.')

return view.tab_settings(message_type=type, message=msg)

from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model
view = context

editable = model.get_editable()
if editable is None:
    type = 'error'
    msg = _("There's no editable version to set the renderer on.")
    return view.tab_settings(message_type=type, message=msg)

if request.form.has_key('renderer_name_select'):
    model.set_renderer_name(request.form['renderer_name_select'])

type = 'feedback'
msg = _('Renderer setting saved.')

return view.tab_settings(message_type=type, message=msg)

from Products.Silva.i18n import translate as _

model = context.REQUEST.model
view = context
REQUEST = context.REQUEST

model.copy_layout()

return view.tab_metadata(
    form_errors={},
    message_type='feedback',
    message=_('Layout copied'))


model = context.REQUEST.model
view = context
REQUEST = context.REQUEST

model.copy_layout()

return view.tab_metadata(
    form_errors={},
    message_type='feedback',
    message='Layout copied')

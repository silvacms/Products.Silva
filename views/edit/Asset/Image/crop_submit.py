from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

try:
    result = view.crop_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

msg = ['Image cropped.']
msg_type = 'feedback'
size = result['size']
x = result['x']
y = result['y']

# i abuse method canScale for detecting PIL here
if model.canScale() and model.canCrop(size, x, y):
    model.cropImage(size, x, y)
else:
    return view.tab_edit(message_type='error', message='The image can not\
 be cropped with the given coordinates. Maybe you selected one of the edges\
 of the image or the dimensions are too large.')
return view.tab_edit(message_type=msg_type, message=' '.join(msg))

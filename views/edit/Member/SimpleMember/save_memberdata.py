## Script (Python) "save_memberdata"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
view = context
request = view.REQUEST
model = request.model

next_view = '%s/edit' % model.absolute_url()

request.SESSION['message_type'] = ''
request.SESSION['message'] = ''

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result = view.memberform.validate_all(request)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    request.SESSION['message_type'] = 'error'
    request.SESSION['message'] = view.render_form_errors(e)
    
    # request.RESPONSE.redirect(next_view)
    return context.redirect()

messages = []
if model.fullname() != result['fullname']:
    model.set_fullname(result['fullname'])
    messages.append('fullname updated')

if model.email() != result['email']:
    model.set_email(result['email'])
    messages.append('e-mail updated')

if len(messages)==0:
    messages.append('Nothing changed.')

request.SESSION['message_type'] = 'feedback'
request.SESSION['message'] = ', '.join(messages)
# request.RESPONSE.redirect(next_view)
return context.redirect()

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
    request.RESPONSE.redirect(next_view)
    return

messages = []
if model.fullname() != result['fullname']:
    model.set_fullname(result['fullname'])
    messages.append('fullname updated')

if model.email() != result['email']:
    model.set_email(result['email'])
    messages.append('e-mail updated')

if model.address() != result['address']:
    model.set_address(result['address'])
    messages.append('address updated')

if model.postal_code() != result['postal_code']:
    model.set_postal_code(result['postal_code'])
    messages.append('postal code updated')

if model.city() != result['city']:
    model.set_city(result['city'])
    messages.append('city updated')

if model.country() != result['country']:
    model.set_country(result['country'])
    messages.append('country updated')

if model.telephone() != result['telephone']:
    model.set_telephone(result['telephone'])
    messages.append('telephone number updated')

if model.fax() != result['fax']:
    model.set_fax(result['fax'])
    messages.append('fax number updated')

if len(messages)==0:
    messages.append('Nothing changed.')

request.SESSION['message_type'] = 'feedback'
request.SESSION['message'] = ', '.join(messages)
request.RESPONSE.redirect(next_view)

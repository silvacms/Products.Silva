from Products.Silva.i18n import translate as _
from zope.i18n import translate

view = context
request = view.REQUEST
model = request.model

next_view = '%s/edit' % model.absolute_url()
request.SESSION['message_type'] = ''
request.SESSION['message'] = ''
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result = view.memberform.validate_all(request)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    request.SESSION['message_type'] = 'error'
    request.SESSION['message'] = view.render_form_errors(e)
    
    return request.RESPONSE.redirect(next_view)
    #return context.redirect()

# validate form
messages = []
if model.fullname() != result['fullname']:
    model.set_fullname(result['fullname'])
    messages.append(translate(_('Full name updated')))

if model.email() != result['email']:
    model.set_email(result['email'])
    messages.append(translate(_('Email updated')))

if result.has_key('editor'):
    if model.editor() != result['editor']:
        model.set_editor(result['editor'])
        messages.append(translate(_('Editor updated')))

if request.has_key('langsetting'):
    languageProvider = context.getLanguageProvider()
    if (str(request['langsetting']) != 
            str(languageProvider.getPreferredLanguage())):
        languageProvider.setPreferredLanguage(request['langsetting'])
        messages.append(translate(_('Language updated')))

if len(messages)==0:
    messages.append(translate(_('Nothing changed.')))

request.SESSION['message_type'] = 'feedback'
request.SESSION['message'] = ', '.join(messages)
return request.RESPONSE.redirect(next_view)
#return context.redirect()

## Script (Python) "tab_docma_export"
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

if not request.has_key('email') or not request['email']:
    return view.tab_docma(message_type='error', message='Enter your e-mail address')

if not request.has_key('doc') or not request['doc']:
    return view.tab_docma(message_type='error', message='Select a file for upload')

description = 'No description'
if request.has_key('description') and request['description']:
    description = request['description']

data = request['doc'].read()

model.service_docma.word2silva(data, str(context.REQUEST['AUTHENTICATED_USER']), request['email'], description)

return view.tab_docma(message_type='feedback', message='Finished importing')

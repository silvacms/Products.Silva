## Script (Python) "tab_edit_word2silva"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=with_sub_publications=0, export_last_version=0
##title=
##
view = context
request = view.REQUEST
model = request.model

if not request.has_key('importfile') or not request['importfile']:
    return view.tab_edit_import(message_type='error', message='Select a file for upload.')

if not getattr( request['importfile'], 'filename', None):
    return view.tab_edit_import(message_type="error", message="Empty or invalid file.")

data = request['importfile'].read()

if not model.xml_validate(data):
    return view.tab_edit(message_type='error',
                         message='Data is not valid Silva XML')

model.xml_import(data)

return view.tab_edit(message_type='feedback', message='Finished importing.')

## Script (Python) "tab_edit_word2silva"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=with_sub_publications=0, export_last_version=0
##title=
##
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model

if not request.has_key('importfile') or not request['importfile']:
    return context.tab_edit_import(message_type='error', message=_('Select a file for upload.'))

if not getattr( request['importfile'], 'filename', None):
    return context.tab_edit_import(message_type="error", message=_("Empty or invalid file."))

data = request['importfile'].read()

if not model.xml_validate(data):
    return context.tab_edit(message_type='error',
                         message=_('Data is not valid Silva XML'))

model.xml_import(data)

return context.tab_edit(message_type='feedback', message=_('Finished importing.'))

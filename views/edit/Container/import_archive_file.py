view = context
request = view.REQUEST
model = request.model

if not request.has_key('importfile') or not request['importfile']:
    return view.tab_edit_import_xml(
        message_type='error', message='Select a file for upload')

feedback = model.archive_file_import(
    request.get('importfile'), request.get('title', ''))

try:
    succeeded, failed = feedback
except:
    # feedback is not a tuple, just a message
    msg = feedback
    message_type='alert'
else:
    msg = []
    message_type='feedback'
    if succeeded:    
        msg.append('Added %s' % view.quotify_list(succeeded))
    else:
        message_type='alert'

    if failed:
        msg.append('<span class="warning">could not add: %s</span>' % view.quotify_list(failed))
    msg = ' '.join(msg)

return view.tab_edit(
    message_type=message_type, message='Finished importing: %s' % msg)

## Script (Python) "tab_status_export_selected_start"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=refs=None
##title=
##
view = context
request = view.REQUEST
model = request.model

if not request.has_key('refs') or not request['refs']:
    return view.tab_status(message_type='error', message='No items were selected, so nothing was exported')
else:
    return view.tab_status_export_selected()

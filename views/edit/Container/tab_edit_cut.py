## Script (Python) "tab_edit_cut"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=None
##title=
##
model = context.REQUEST.model
view = context

if ids is None:
    return view.tab_edit(message_type="error", message="Nothing was selected, so nothing was cut.")

cut_ids = []
not_cut_ids = []
message_type = 'feedback'
for id in ids:
    if model.is_delete_allowed(id):
        cut_ids.append(id)
    else:
        not_cut_ids.append(id)
 
model.action_cut(ids, context.REQUEST)

if cut_ids:
    if not_cut_ids:
        message = 'Placed %s on clipboard for cutting, <span class="error">but could not cut %s.</span>' % (view.quotify_list(cut_ids), view.quotify_list(not_cut_ids))
    else:
        message = 'Placed %s on clipboard for cutting.' % view.quotify_list(cut_ids)
else:
    message = 'Could not place %s on clipboard for cutting.' % view.quotify_list(not_cut_ids)
    message_type = 'error'

return view.tab_edit(message_type=message_type, message=message)

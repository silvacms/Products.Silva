##parameters=groups=[]
request = context.REQUEST
model = request.model
view = context

if not groups:
    return view.tab_edit(
        message_type="error", message="No group selected, so nothing copied.")

copied = model.copyIPRangesFromIPGroups(groups)
if copied:
    message = "Range(s) %s added." % view.quotify_list(copied)
    type = 'feedback'
else:
    message = "Nothing copied."
    type = 'error'
return view.tab_edit(message_type=type, message=message)


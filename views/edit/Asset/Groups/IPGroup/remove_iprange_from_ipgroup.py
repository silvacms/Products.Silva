##parameters=ipranges=[]
request = context.REQUEST
model = request.model
view = context

if not ipranges:
    return view.tab_edit(
        message_type="error", message="No ip ranges selected, so none removed.")
removed = []
for iprange in ipranges:
    model.removeIPRange(iprange)
    removed.append(iprange)
removed = view.quotify_list(removed)
message = "Range(s) %s removed from the group." % removed
return view.tab_edit(message_type="feedback", message=message)


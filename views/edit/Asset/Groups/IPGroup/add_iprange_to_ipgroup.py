##parameters=iprange
request = context.REQUEST
model = request.model
view = context

if not iprange:
    return view.tab_edit(
        message_type="error", message="No ip range given, so none added.")

try:
    model.addIPRange(iprange)
except ValueError, e:
    message = str(e)
    type = 'error'
else:
    message = "Range %s added to the IP Group" % view.quotify(iprange)
    type = 'feeback'
return view.tab_edit(message_type=type, message=message)


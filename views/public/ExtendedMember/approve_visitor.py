## Script (Python) "approve_visitor"
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

if not model.email() or not model.fullname():
    request.SESSION['message_type'] = 'error'
    request.SESSION['message'] = 'At least the full name and e-mail address are required to approve someone!'
    request.RESPONSE.redirect(model.absolute_url())
    return

model.approve()

request.SESSION['message_type'] = 'feedback'
request.SESSION['message'] = 'Member is approved'

request.RESPONSE.redirect(model.absolute_url())

## Script (Python) "approve_visitor"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.i18n import translate as _
from zope.i18n import translate

request = context.REQUEST
model = request.model
next_view = '%s/edit' % model.absolute_url()

if not model.email() or not model.fullname():
    request.SESSION['message_type'] = 'error'
    request.SESSION['message'] = '<dl>\n<dt>' + translate(_('Sorry, content is missing:')) + '\n<dd><span class="error">' + unicode(_('Both a name and e-mail address are required to approve someone.')) + '</span></dd>\n</dl>'
    request.RESPONSE.redirect(next_view)
    return

model.approve()

request.SESSION['message_type'] = 'feedback'
request.SESSION['message'] = _('Member is approved')

request.RESPONSE.redirect(next_view)

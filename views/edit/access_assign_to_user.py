## Script (Python) "access_assign_to_user"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userids=None, assign_role=None
##title=
##
from Products.Silva.i18n import translate as _

request = context.REQUEST
if not assign_role or assign_role == 'None':
    return context.tab_access(message_type="error", message=_("No role selected."))

if not userids:
    return context.tab_access(message_type="error", message=_("No user(s) selected."))

model = request.model
#assigned = []
for userid in userids:
    try:
        model.sec_assign(userid, assign_role)
    except:
        # No feedback, can't have the exception with a lot of bad things.
        # Stay silent until we got a better framework.
        pass
    #assigned.append((userid, assign_role))

#return context.tab_access(
#    message_type="feedback",
#    message="Role(s) assigned") # for %s" % context.quotify_list_ext(assigned))

# FIXME: do we need feedback?
request.RESPONSE.redirect('%s/edit/tab_access' % model.absolute_url())

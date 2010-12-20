## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.i18n import translate as _

version = context.REQUEST.model
result = version.render_view()
if result is None:
    msg = _("This ghost is broken. (${haunted_url})",
            mapping={'haunted_url': version.get_haunted_url()})
    return msg
else:
    return result

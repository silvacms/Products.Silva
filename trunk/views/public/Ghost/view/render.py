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
   return _("This 'ghost' document is broken. Please inform the site administrator.")
else:
   return result

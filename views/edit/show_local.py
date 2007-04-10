## Script (Python) "show_local"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# Example code:

# Import a standard function, and get the HTML request and response objects.
from Products.Silva.i18n import translate as _
from Products.PythonScripts.standard import html_quote
request = container.REQUEST
RESPONSE =  request.RESPONSE

# Return a string identifying this script.
msg = _('This is the ${meta_type} "${id}"',
        mapping={'meta_type': script.meta_type, 'id': script.getId()})
print msg,
if script.title:
    print "(%s)" % html_quote(script.title),
print _("in"), container.absolute_url()
return printed

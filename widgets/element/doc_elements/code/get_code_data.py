## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
code = context.get_code_object()

if not code:
    return '<span class="warning">[Code element is broken]</span>'

# this is also done in get_code(), but I need to get to path:
node = context.REQUEST.node
path = node.getAttribute('path')

return 'Code element: %s at %s' % (code.title_or_id(), path)


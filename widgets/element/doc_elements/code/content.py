## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
path = node.output_convert_html(node.getAttribute('path'))
code = None
if path:
    try:
        code = node.restrictedTraverse(path)
    except (KeyError, AttributeError):
        # reference is broken
        return '<span class="warning">[code element %s cannot be found]</span>' % path
else:
    return '<span class="warning">[No code element selected]</span>'

return 'Code element: %s at %s' % (code.title_or_id(), path)


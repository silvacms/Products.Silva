node = context.REQUEST.node
path = node.output_convert_html(node.getAttribute('path'))
if path:
    try:
        code = node.restrictedTraverse(str(path))
    except (KeyError, AttributeError):
        # reference is broken
        return '<span class="warning">[code element %s cannot be found]</span>' % path
else:
    return '<span class="warning">[No code element selected]</span>'

return code()

node = context.REQUEST.node
path = node.output_convert_html(node.getAttribute('path'))

if path:
    try:
        path = str(path)
        code = node.restrictedTraverse(path)
        return code
    except (KeyError, AttributeError):
        # reference is broken
        return None

request = context.REQUEST
node = request.node
path = node.getAttribute('path').encode('ascii')
datasource = None

if path:
    try:
        datasource = node.restrictedTraverse(path)
    except (KeyError, AttributeError, ValueError, IndexError):
        # datasource reference is broken (i.e. renamed)
        return None

return datasource
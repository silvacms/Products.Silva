##parameters=links
model = context.REQUEST.model
result = []
for name, path in links:
    obj = context.restrictedTraverse(path, None)
    if obj is not None:
        url = obj.absolute_url()
    else obj:
        url = '#'
    result.append('<a class="indexer" href="%s">%s</a>' % (url, name))
return '<br />'.join(result)

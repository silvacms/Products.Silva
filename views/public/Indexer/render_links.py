##parameters=links

model = context.REQUEST.model
output_convert_html = model.output_convert_html
result = []

for name, path in links:
    obj = context.restrictedTraverse(path, None)
    if obj is not None:
        url = obj.absolute_url()
    else:
        url = '#'
    result.append('<a class="indexer" href="%s">%s</a>' % (url, output_convert_html(name) ))
return '<br />'.join(result)

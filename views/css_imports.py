##parameters=imports=None

if imports is None:
    return

request = context.REQUEST
model = request.model
root_url = model.get_root_url()

result = []
for css in imports:
    result.append('@import url(%s/globals/%s);' % (root_url, css))

return '\n%s\n' % '\n'.join(result)
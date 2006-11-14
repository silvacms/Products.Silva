##parameters=name, links

from Products.Silva.mangle import generateAnchorName

result = []
for title, path, name in links:
    obj = context.restrictedTraverse(path, None)
    if obj is not None:
        url = obj.absolute_url()
    else:
        url = '#'
    result.append(
        '<a class="indexer" href="%s#%s">%s</a>' % (
        url, name, title))
return '<br />'.join(result)

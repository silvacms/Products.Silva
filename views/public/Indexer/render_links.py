## Script (Python) "render_links"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=links
##title=
##
model = context.REQUEST.model
output_convert_html = model.output_convert_html

result = []
for name, url in links:
    result.append('<a href="%s">%s</a>' % (url, output_convert_html(name)))
return '<br />'.join(result)

##parameters=view_method='view'
content = 'content.html'
override = 'override.html'

# By default, the rendering is done by 'content', unless 
# a local 'override' exists (disregarding acquisition).
if hasattr(context.aq_explicit, override):
    renderer = override
else:
    renderer = content

# Setting Headers first
context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html;charset=utf-8')
context.REQUEST.RESPONSE.setHeader('Cache-Control','max-age=300')


## use layout content if a layout has been setup
if renderer == content:
    layout_folder = context.get_layout_folder()
    if layout_folder:
        index = getattr(layout_folder, content)
        return index(model=context, view_method=view_method)


# By default, the prefered view method is 'view()', unless
# a different view_method is passed to this script.
return getattr(context, renderer)(view_method=view_method)

## Script (Python) "get_edit_mode"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
view = context
request = view.REQUEST
model = request.model

response = request.RESPONSE
headers = [('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT'),
            ('Last-Modified', 
                DateTime("GMT").strftime("%a, %d %b %Y %H:%M:%S GMT")),
            ('Cache-Control', 'no-cache, must-revalidate'),
            ('Cache-Control', 'post-check=0, pre-check=0'),
            ('Pragma', 'no-cache'),
            ]

placed = []
for key, value in headers:
    if key not in placed:
        response.setHeader(key, value)
        placed.append(key)
    else:
        response.addHeader(key, value)


response.setHeader('Content-Type', 'text/html;charset=utf-8')
docref = model.create_ref(model)
xhtml = model.editor_storage(editor='kupu')

return ('<html>\n'
        '<head>\n'
        '<title>%s</title>\n'
        '<link type="text/css" rel="stylesheet" href="%s" />\n'
        '<link type="text/css" rel="stylesheet" href="%s" />\n'
        '<link type="text/css" rel="stylesheet" href="override_editor.css" />\n'
        '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n'
        '<meta name="docref" content="%s" />\n'
        '</head>\n'
        '%s\n'
        '</html>' % (model.get_title_editable(), 
                        getattr(context, 'frontend.css').absolute_url(),
                        getattr(context.globals, 'kupu.css').absolute_url(),
                        docref,
                        xhtml))

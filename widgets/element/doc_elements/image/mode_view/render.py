## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
image_id = str(node.getAttribute('image_id'))
if not image_id:
  return '<p class="error">[No image selected]</p>'
image = getattr(node.get_content().get_container(), image_id, None)
if not image:
  return '<p class="error">[Image broken]</p>'
return '<p>%s</p>' % image.view()

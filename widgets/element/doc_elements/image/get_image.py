## Script (Python) "get_image"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=image_context, image_path
##title=
##
try:
    # To fix this for Zope 2.5.1
    if image_path.startswith('/'):
        path = str(image_path)
    else:
        image_path = tuple(str(image_path).split('/'))
        context_path = image_context.getPhysicalPath()
        path = '/'.join(context_path + image_path)
    image = image_context.restrictedTraverse(path)

except (KeyError, AttributeError, ValueError, IndexError):
    # image reference is broken (i.e. renamed)
    image = None
if getattr(image, 'meta_type', None) != 'Silva Image':
    image = None
return image


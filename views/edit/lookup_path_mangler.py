##bind context=context
##parameters=obj_context, obj
# $Id: lookup_path_mangler.py,v 1.1 2003/06/06 09:57:34 guido Exp $

obj_context = obj_context.split('/')
obj_path = obj.getPhysicalPath()
return '/'.join(context.path_mangler(obj_context, obj_path))


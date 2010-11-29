##bind context=here
##parameters=object
# $Id: is_title_editable.py,v 1.2 2003/10/16 16:08:42 jw Exp $
if object.implements_container():
    object.can_set_title()
#    default = here.get_default(object)
#    if default is None:
#        return 1
#    else:
#        return 0
return 1


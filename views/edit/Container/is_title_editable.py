##bind context=view
##parameters=object
# $Id: is_title_editable.py,v 1.1 2003/07/28 10:00:16 zagy Exp $
if object.implements_container():
    default = view.get_default(object)
    if default is None:
        return 1
    else:
        return 0
return 1


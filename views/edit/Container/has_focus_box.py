## Script (Python) "has_focus_box"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=tab_id
##title=
##
if tab_id == 'add_contactinfo' or 'add_course' or 'add_document' or 'add_folder' or 'add_ghost' or 'add_image' or 'add_publication':
    return 1
else:
    return 0

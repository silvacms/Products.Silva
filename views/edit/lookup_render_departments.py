## Script (Python) "lookup_render_departments"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member
##title=
##
if not member.departments():
    return '-'
else:
    return ', '.join(member.departments())

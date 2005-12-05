## Script (Python) "get_link_status_text"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ghost_version
##title=
##
from Products.Silva.i18n import translate as _

status = ghost_version.get_link_status()
if status == ghost_version.LINK_OK:
    return ''
elif status == ghost_version.LINK_EMPTY:
    return _('You have to enter a path here.')
elif status == ghost_version.LINK_VOID:
    msg = _('The object &#xab;${haunted_url}&#xbb; the ghost points to does '
            'not exist.')
elif status == ghost_version.LINK_FOLDER:
    msg = _('The object &#xab;${haunted_url}&#xbb; the ghost points to is a '
            'container.')
elif status == ghost_version.LINK_GHOST:
    msg = _('The object &#xab;${haunted_url}&#xbb; the ghost points to is '
            'itself a ghost.')
elif status == ghost_version.LINK_NO_CONTENT:
    msg = _('The object &#xab;${haunted_url}&#xbb; the ghost points to is '
            'not a content object.')
elif status == ghost_version.LINK_CONTENT:
    msg = _('The object &#xab;${haunted_url}&#xbb; the ghost points to is a '
            'content object.')
elif status == ghost_version.LINK_NO_FOLDER:
    msg = _('The object &#xab;${haunted_url}&#xbb; the ghost points to is '
            'not a container.')
elif status == ghost_version.LINK_CIRC:
    msg = _('The object &#xab;${haunted_url}&#xbb; the ghost points to is '
            'either the ghost itself or an ancestor of the ghost.')
else:
    return _('The ghost is in an undefined state.')
msg.set_mapping({'haunted_url': ghost_version.get_haunted_url()})
return msg


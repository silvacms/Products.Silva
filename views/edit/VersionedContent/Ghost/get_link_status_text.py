## Script (Python) "get_link_status_text"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ghost_version
##title=
##
status = ghost_version.get_link_status()
if status == ghost_version.LINK_OK:
  return ''
elif status == ghost_version.LINK_EMPTY:
  return 'A path must be filled in above.'
elif status == ghost_version.LINK_VOID:
  return "The ghost points to an object that doesn't exist (%s)." %  \
    ghost_version.get_content_url()
elif status == ghost_version.LINK_FOLDER:
  return "The ghost points to a folder (%s). Folders can't be ghosted. Try adding 'index' to the path." % \
    ghost_version.get_content_url()
elif status == ghost_version.LINK_GHOST:
  return 'The ghost points to another ghost (%s). Please ghost the original.' % \
    ghost_version.get_content_url()
elif status == ghost_version.LINK_NO_CONTENT:
  return 'The ghost points to an item that is not content (%s).' % \
    ghost_version.get_content_url()
return 'The ghost is in an undefined state.'

## Script (Python) "tab_edit_revoke_approval"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=version_title
##title=
##

""" This is a rather cryptic solution for a number of problems:
    the first is that the contents of this a string that is used
    as the 'title' attribute of some link needs to get translated,
    which can't be done from PT (_() calls aren't available in
    pagetemplates, and the i18nextract tools don't check for them),
    hence the Python script. The second problem is that the string
    contains non-ascii chars, and the script is written in a UTF-8
    editor, so the string becomes a UTF-8 string, which the
    MessageIDFactory can't work with, hence the 'unicode()' call.
    Last but not least, if we'd just do:

        s = 'view «${version_title}»'
        msg = _(unicode(s, 'UTF-8'))

    the i18nextract tool wouldn't be able to pick the string literal
    from this script, hence the weird construction with mapping a
    lambda to _.
"""
# import the messageidfactory, note that we *don't* map it to _ because
# we need the _ name for our little scheme
from Products.Silva.i18n import translate

# the lambda to have a _() call around the string literal
_ = lambda x: x

# create the message with the _() call around it (for the i18nextract tool)
msg = _('view "${version_title}"')

# turn it to unicode so the messageidfactory can handle it
msg = unicode(msg, 'UTF-8')

# now get a messageid with the contents and interpolate the variable
msg = translate(msg,
                mapping={'version_title': version_title})

# return the interpolated messageid, translation will be done on
# stringification
return msg
